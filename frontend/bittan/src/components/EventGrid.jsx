import React, { useEffect, useState } from "react";
import { Card, Col, Row, Button, Dropdown } from "react-bootstrap";
import axiosInstance from "../api/axiosConfig";

import "./EventGrid.css";

const basename = process.env.PUBLIC_URL || "";

const EventGrid = () => {
	const [upcomingEvents, setUpcomingEvents] = useState([]);
	const [pastEvents, setPastEvents] = useState([]);
	const [showPast, setShowPast] = useState(false);

	useEffect(() => {
		// Fetch events from the backend

		axiosInstance.get("/get_chapterevents/?format=json").then((response) => {
			setUpcomingEvents(response.data.chapter_events);
			setPastEvents(response.data.chapter_events);
		});
	}, []);

	return (
		<>
			<Row className="row">
				{upcomingEvents.map((event) => (
					<Col className="col" key={event.id}>
						<Card className="card">
							{/* If `event.image` is unavailable, display a placeholder */}
							<Card.Img
								variant="top"
								src={event.image || basename + "/earhart_poster.png"}
								alt={event.title}
								style={{height: "auto", width: "20vw", backgroundColor: "transparent"}}
							/>
							<Card.Body className="card-body">
								<Card.Title className="card-title">{event.title}</Card.Title>
								<Card.Text className="card-text">
									{new Date(event.event_at).toLocaleString("sv-SE", {
										weekday: "long",
										year: "numeric",
										month: "long",
										day: "numeric",
										hour: "numeric",
										minute: "2-digit",
										hour12: false,
										})}
								</Card.Text>
								<Button href={`${basename}/events/${event.id}`} className="button">
									Se mer
								</Button>
							</Card.Body>
						</Card>
					</Col>
				))}
			</Row>
		{/*<Dropdown>
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
							href={`${basename}/events/${event.id}`}
							className="dropdown-item"
						>
							{event.title}
						</Dropdown.Item>
					))}
				</Dropdown.Menu>
			</Dropdown>*/}
		</>
	);
};

export default EventGrid;
