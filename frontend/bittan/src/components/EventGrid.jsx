import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Button, Dropdown } from 'react-bootstrap';
import axiosInstance from '../api/axiosConfig';

const EventGrid = () => {
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [pastEvents, setPastEvents] = useState([]);
  const [showPast, setShowPast] = useState(false);

  useEffect(() => {
    // Fetch events from the backend
    axiosInstance.get('/events/').then((response) => {
      setUpcomingEvents(response.data.upcoming);
      setPastEvents(response.data.past);
    });
  }, []);

  return (
    <>
      <Row>
        {upcomingEvents.map((event) => (
          <Col key={event.id} md={4}>
            <Card>
              <Card.Img variant="top" src={event.image} />
              <Card.Body>
                <Card.Title>{event.title}</Card.Title>
                <Card.Text>{event.time}</Card.Text>
                <Button href={`/events/${event.id}`}>View Details</Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
      <Dropdown>
        <Dropdown.Toggle variant="secondary" id="dropdown-basic">
          {showPast ? 'Hide' : 'Show'} Past Events
        </Dropdown.Toggle>
        <Dropdown.Menu show={showPast}>
          {pastEvents.map((event) => (
            <Dropdown.Item key={event.id} href={`/events/${event.id}`}>
              {event.title}
            </Dropdown.Item>
          ))}
        </Dropdown.Menu>
      </Dropdown>
    </>
  );
};

export default EventGrid;
