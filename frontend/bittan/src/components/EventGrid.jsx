// src/components/EventGrid.js
import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Button } from 'react-bootstrap';
import axiosInstance from '../api/axiosConfig';

const EventGrid = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    axiosInstance
      .get('/get_chapterevents/')
      .then((response) => {
        setEvents(response.data);
      })
      .catch((error) => {
        console.error('Error fetching events:', error);
      });
  }, []);

  return (
    <Row>
      {events.map((event) => (
        <Col key={event.id} md={4}>
          <Card className="mb-4">
            <Card.Body>
              <Card.Title>{event.title}</Card.Title>
              <Card.Text>{event.description}</Card.Text>
              <Card.Text>
                {new Date(event.event_at).toLocaleString()}
              </Card.Text>
              <Button variant="primary" href={`/events/${event.id}`}>
                View Details
              </Button>
            </Card.Body>
          </Card>
        </Col>
      ))}
    </Row>
  );
};

export default EventGrid;
