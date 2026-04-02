import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axiosInstance from "../api/axiosConfig";
import FormComponent from "./FormComponent";
import { submitForm } from "../api/submitForm";
import { Alert, Button } from "react-bootstrap";

const EventForm = () => {
	const navigate = useNavigate();
	const { event_id, session_id } = useParams();
	const [initError, setInitError] = useState(false);
	const [initErrorDesc, setInitErrorDesc] = useState("");
	const [submissionError, setSubmissionError] = useState("");
	const [questions, setQuestions] = useState([]);
	const [answersFromSession, setAnswersFromSession] = useState({});
	const [isDisabled, setIsDisabled] = useState(false);
	const [chapterEvent, setChapterEvent] = useState();
	const [sessionStatus, setSessionStatus] = useState();
	const [email, setEmail] = useState();

	useEffect(() => {
		axiosInstance.get(`/get_chapterevents/${event_id}`).then((response) => {
			const event_data = response.data.chapter_event;
			if (response.data.questions.length !== 0) {
				setQuestions(response.data.questions);
			} else {
				throw new Error("NoForm")
			}

			setChapterEvent(event_data);
			if (Date.now() > Date.parse(event_data.sales_stop_at)) setIsDisabled(true);

			return axiosInstance.get(`/get_session/${session_id}/`)
		}).then((response) => {
				const session_info = response.data;
				setAnswersFromSession(Object.fromEntries(session_info.answers.map((val, index) => [val.question_id, val])));	
				setSessionStatus(session_info.status);
				setEmail(session_info.email)

				//if (session_info.status === "CONFIRMED") navigate(`/Payment/${session_id}`);

				if (!["FORM_SUBMITTED", "RESERVED", "FAILED_EXPIRED_RESERVATION"].includes(session_info.status)) {
					setIsDisabled(true);
				}		

				setInitError(false);
		}).catch((e) => { 
			setInitError(true);
			if (e.message === "NoForm") {
				setInitErrorDesc("Kunde inte hitta enkät");
			} else if (e.status === 404) {
			setInitErrorDesc(`Kunde inte hitta 
				${e.response.config.url.includes("get_chapterevents") ? "evenemang" : "anmälan"}
				med identifierare ${e.response.config.url.includes("get_chapterevents") ? event_id : session_id}`);
			} else {
				setInitErrorDesc("Okänt fel");
			}
		});
	}, []);

	const handleSubmit = (formData) => {
		submitForm(session_id, Object.values(formData)).then(() => {
			if (chapterEvent.fcfs) 	navigate(`/Payment/${session_id}`);
			setSubmissionError("")
			setSessionStatus("FORM_SUBMITTED")	
		}).catch( (e) => {
			if (e.status === 500) setSubmissionError("Något gick fel när formuläret besvarades")

			const errorRes = e.response.data
			if (errorRes === "AlreadyPaidPayment") setSubmissionError("Kan inte besvara formulär för en betalad biljett")
			else if (errorRes === "FormClosed") setSubmissionError("Formuläret är stängt och kan inte längre besvaras eller ändras")
			else if (errorRes === "SessionExpired") setSubmissionError("Formuläret har gått ut och biljetterna är slut") // Du var för trög din jäkel, försök igen dumbom.
			else setSubmissionError("Något gick fel när formuläret besvarades")
		})
	};

	const handleGoToPayment = () => navigate(`/Payment/${session_id}`);
	
	if (initError) return (
		<>
			<span> Följande fel inträffade: {initErrorDesc}. Försök igen.  </span>
		</>
	)
	return (
		<>
			<FormComponent 
				questions={questions} 
				onSubmit={handleSubmit} 
				initialFormData={answersFromSession} 
				submissionError={submissionError}
				disabled={isDisabled}
			/>
      {submissionError !== "" && <Alert className="mt-2" variant="danger"> {submissionError} </Alert>}
			{sessionStatus === "CONFIRMED" && 
				<>
					<Alert className="mt-2" variant="success"> 
						Grattis, du har fått en plats. Det går tyvärr inte längre att redigera dina formulärsvar. Om du vill ändra något så kontakta arrangören av 
						evenemanget.
					</Alert>
					<Button variant="primary" onClick={handleGoToPayment}> Vidare till betalning </Button>
				</>
			}
			{ sessionStatus === "FORM_SUBMITTED" &&
				<Alert className="mt-2" variant="success">
					Din anmälan är skickad. Bekräftelse på anmälan finns skickad till {email}. Ändringar kan göras fram tills 
					platsbekräftelse på denna sida eller länken i mailet.  
				</Alert>
			}
		</>
	);
};

export default EventForm;
