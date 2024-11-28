import React, { useEffect, useState } from "react";
import { Card, Col, Row, Button, Dropdown } from "react-bootstrap";
import axiosInstance from "../api/axiosConfig";

import "./EventGrid.css";

const EventGrid = () => {
	const [upcomingEvents, setUpcomingEvents] = useState([]);
	const [pastEvents, setPastEvents] = useState([]);
	const [showPast, setShowPast] = useState(false);

	useEffect(() => {
		// Fetch events from the backend

		axiosInstance.get("/get_chapterevents/").then((response) => {
			setUpcomingEvents(response.data);
			setPastEvents(response.data);
		});
	}, []);

	const EventTime = ({ datetime }) => {
		const localTime = new Date(datetime).toLocaleString("en-US", {
			weekday: "long",
			year: "numeric",
			month: "long",
			day: "numeric",
			hour: "numeric",
			minute: "2-digit",
			hour12: false, // Change to false for 24-hour format
		});

		return <p className="event-time">{localTime}</p>;
	};

	return (
		<>
			<Row className="row">
				{upcomingEvents.map((event) => (
					<Col className="col" key={event.id}>
						<Card className="card">
							{/* If `event.image` is unavailable, display a placeholder */}
							<Card.Img
								variant="top"
								src={event.image || "https://via.placeholder.com/150"}
								alt={event.title}
							/>
							<Card.Body className="card-body">
								<Card.Title className="card-title">{event.title}</Card.Title>
								<EventTime datetime={event.event_at} />
								<Button href={`/events/${event.id}`} className="button">
									Book tickets
								</Button>
							</Card.Body>
						</Card>
					</Col>
				))}
			</Row>
			<Dropdown>
				<Dropdown.Toggle
					variant="secondary"
					id="dropdown-basic"
					className="dropdown-toggle"
				>
					{showPast ? "Hide" : "Show"} Past Events
				</Dropdown.Toggle>
				<Dropdown.Menu className="dropdown-menu" show={showPast}>
					{pastEvents.map((event) => (
						<Dropdown.Item
							key={event.id}
							href={`/events/${event.id}`}
							className="dropdown-item"
						>
							{event.title}
						</Dropdown.Item>
					))}
				</Dropdown.Menu>
			</Dropdown>
		</>
	);
};

export default EventGrid;
