import { useNavigate, useParams } from "react-router-dom";
import React, { useState, useEffect } from "react";
import { useLocation, Link } from "react-router-dom";
import { startPayment } from "../api/startPayment";
import { sessionPaymentStatus } from "../api/sessionPaymentStatus";
import { generateQR } from "../api/generateQR";
import { Container, Row, Col } from "react-bootstrap";
import axiosInstance from "../api/axiosConfig";

const basename = process.env.PUBLIC_URL || "";

const Payment = () => {
  const location = useLocation();
  const { session_id } = useParams();
  const [ email, setEmail ] = useState();
  const [ totalAmount, setTotalAmount ] = useState(); 
  const [ chosenTickets, setChosenTickets ] = useState([]);
  const [ swishToken, setSwishToken ] = useState(null);
  const [ chapterEvent, setChapterEvent ] = useState({});
  const [ qrUrl, setQrUrl ] = useState(null);
  const [ isMobile, setIsMobile ] = useState(false);
  const [ status, setStatus ] = useState("pending");
  const [ isChecked, setIsChecked ] = useState(false);
  const [ eventQuestions, setEventQuestions ] = useState([]);
  const [ formAnswers, setFormAnswers ] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    let interval;

    const fetchStatus = async () => {
      try {
        const response = await sessionPaymentStatus(session_id);
        if (response.status === "PAID") {
          clearInterval(interval);
          navigate("/booking-confirmed", { state: { mail: response.mail, status: response.status, reference: response.reference } });
          setStatus("paid")
        } else if(response.status == "FAILED_EXPIRED_RESERVATION") {
          clearInterval(interval);
          setStatus("timed_out")
        }
        // The payment must have faild if it is neither reserved nor paid
        // The payment is failed if it is not either RESERVED, CONFIRMED, or PAID at this step. 
        else if ( !["RESERVED", "CONFIRMED"].includes(response.status)) {
          clearInterval(interval);
          setStatus("failed")
        }
      } catch (error) {
        console.error("Error fetching payment status:", error);
      }
    };

    interval = setInterval(fetchStatus, 1000);
    fetchStatus();

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setIsMobile(/Mobi|Android/i.test(navigator.userAgent));
    axiosInstance.get(`/get_session/${session_id}/`).then((response) => {
      const session_data = response.data;
      setEmail(session_data.email);
      setFormAnswers(session_data.answers)
      setTotalAmount(session_data.total_price)
      axiosInstance.get(`/get_chapterevents/${session_data.chapter_event}`).then( (innerResponse) => {
        const event_data = innerResponse.data.chapter_event; 
        setChapterEvent(event_data);
        setEventQuestions(innerResponse.data.questions);
        
        const ticket_types = innerResponse.data.ticket_types;
        const session_tickets = new Map(session_data.tickets.map(item => [item.ticket_type, item]));
        const chosen_tickets = ticket_types.map(ticket => {
          const matchingTicket = session_tickets.get(ticket.id);
          return {
            title: ticket.title,
            price: ticket.price,
            ticket_type: ticket.id, 
            count: matchingTicket ? matchingTicket.count : 0
          }
        });
        setChosenTickets(chosen_tickets)
      }).catch((e) => console.log(e)) 
    }) 
  }, []);

  const handlePayment = async (sameDevice) => {
    try {
      let token = swishToken;
      if(!swishToken) {
        token = await startPayment(email, session_id);
        setSwishToken(token);
      }

      if (sameDevice) {
        window.location = `swish://paymentrequest?token=${token}`;
      } else {
        const response = await generateQR(token);
        const blob = new Blob([response], { type: 'image/png' });
        const qrCodeUrl = URL.createObjectURL(blob);
        setQrUrl(qrCodeUrl);
      }
    } catch (error) {
      console.error("Payment failed", error);
    }
  };

  const renderAnswerOverivew = () => {
    if (!formAnswers || formAnswers.length === 0) return 
  
    const table_rows = formAnswers.reduce( (acc, answer) => {
      const question = eventQuestions.find(q => q.id === answer.question_id);

      const question_rows =  answer.option_ids.map((optionId, index) => {
        const option = question.options.find(opt => opt.id === optionId);

        const text = option.has_text ? answer.option_texts[index] : option.name

        return {
          questionTitle: question.title,
          displayText: text,
          price: option.price
        }
      }).filter(Boolean)
      
      if (question_rows.length > 0) {
        acc.push({
          questionTitle: question.title, 
          rows: question_rows
        })
      }
      return acc
    }, [])

    return (
      <Container className="mb-4 small">
      { table_rows.map((group, i) => (
        <React.Fragment>
        {group.rows.map((row, rowIndex) => 
          <Row key={rowIndex} className={` py-2 ${rowIndex === 0 && i !== 0 ? 'border-top' : ''}`}>
          {rowIndex === 0 ? (
            <Col>
            {group.questionTitle}
            </Col>
          ) : (
            <Col></Col>
          )}
          <Col>{row.displayText}</Col>
          <Col>{row.price !== 0 ? `${row.price} kr` : ''}</Col>
          </Row>    
        )}
        </React.Fragment>
      ))
      }
      </Container>
    ) 
  }

  return (
    <div>
      <h2>Betalning</h2>
    
    <h4>{chapterEvent.title}</h4>
    <Container style={{maxWidth: "400px", float: "left"}}>
        {chosenTickets.filter((ticket) => ticket.count > 0).map((ticket) => (
          <>
          <Row key={ticket.ticket_type} style={{ marginBottom: "8px" }}>
            <Col className="text-left">{ticket.title}:</Col>
            <Col className="text-left">{ticket.count}st</Col>
            <Col className="text-left">{ticket.price}kr</Col>
          </Row>
          {renderAnswerOverivew()}
          </>
        ))}
        <Row className="py-1">
          <Col className="text-left">
            Totalt: {totalAmount} kr (Moms 0 kr)
          </Col>
        </Row>
      
      {status != "pending" &&
            <Row>
              <p>Betalningen misslyckades</p>
              {status == "timed_out" && <Container>Betalningen tog för lång tid eller så nekades betalningen</Container>}
              <p>Gå tillbaka till <Link to="/">huvudsidan</Link> och försök beställa igen.</p>
            </Row>
      }
      
      {status == "pending" && <Container>
        <Row>
          <label>
            <input type="checkbox" checked={isChecked} onChange={() => setIsChecked(!isChecked)} />
            {" "}Jag godkänner <a href="https://drive.google.com/file/d/1biyd25AMdVJPcGlvS7PUojpc-Lj2jfDV/view" target="_blank" rel="noopener noreferrer">köpesvillkoren</a>{" "}och <a href="https://drive.google.com/file/d/1QmSgQAUfbS3sNTTLKmy2FBEiG3nloCSl/view" target="_blank" rel="noopener noreferrer">Personuppgiftspolicy</a>
          </label>
        </Row>
          { status != "pending" &&
            <div>
                <Row>
                  Betalning misslyckades
                </Row>
                { status == "timed_out" && 
                  <Row>
                    Du var för trög din jäkel. Försök igen dumbom
                  </Row>
                }
            </div>
          }
          {!qrUrl && (
            <div>
              <Row className="py-1">
                <button onClick={() => handlePayment(true)} className="btn btn-primary" disabled={!isChecked || status != "pending"}>
                  Betala med Swish på denna enhet
                </button>
              </Row>
              <Row className="py-1">
                <button onClick={() => handlePayment(false)} className="btn btn-primary" disabled={!isChecked || status != "pending"}> 
                  Betala med Swish på annan enhet 
                </button>
              </Row>
            </div>
          )}
          {qrUrl && (
              <Row className="py-1">
                <p>Skanna QR-koden i Swishappen:</p>
                <img src={qrUrl} alt="Swish QR Code" />
              </Row>
          )}
          <Row>
            <p>Du skickas tillbaka till denna sida efter att du betalat. Har du betalat omdirigeras du inom kort.</p>
          </Row>
        </Container>
      }
      </Container>
    </div>
  );
};

export default Payment;
