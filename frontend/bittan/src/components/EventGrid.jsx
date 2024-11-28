import React, { useEffect, useState } from 'react';
import { Card, Col, Row, Button, Dropdown } from 'react-bootstrap';
import axiosInstance from '../api/axiosConfig';

import './EventGrid.css';

const EventGrid = () => {
  const [upcomingEvents, setUpcomingEvents] = useState([]);
  const [pastEvents, setPastEvents] = useState([]);
  const [showPast, setShowPast] = useState(false);

  const testData = {
    upcoming: [
      {
      "id": 1,
      "title": "Fysikalen Dag 1",
      "description": "1 dagen av Fysikalen.",
      "event_at": "2025-10-31T18:21:39.396186+01:00"
    },
    {
      "id": 2,
      "title": "Fysikalen Dag 2",
      "description": "2 dagen av Fysikalen.",
      "event_at": "2025-11-01T18:21:39.396186+01:00"
    },
    {
      "id": 3,
      "title": "Fysikalen Dag 3",
      "description": "3 dagen av Fysikalen.",
      "event_at": "2025-11-02T18:21:39.396186+01:00"
    },
    {
      "id": 4,
      "title": "Fysikalen Dag 4",
      "description": "4 dagen av Fysikalen.",
      "event_at": "2025-11-03T18:21:39.396186+01:00"
    },
    {
      "id": 5,
      "title": "Fysikalen Dag 5",
      "description": "5 dagen av Fysikalen.",
      "event_at": "2025-11-04T18:21:39.396186+01:00"
    },
    {
      "id": 6,
      "title": "Fysikalen Dag 6",
      "description": "6 dagen av Fysikalen.",
      "event_at": "2025-11-05T18:21:39.396186+01:00"
    },
    {
      "id": 7,
      "title": "Fysikalen Dag 7",
      "description": "7 dagen av Fysikalen.",
      "event_at": "2025-11-06T18:21:39.396186+01:00"
    },
    {
      "id": 8,
      "title": "Fysikalen Dag 8",
      "description": "8 dagen av Fysikalen.",
      "event_at": "2025-11-07T18:21:39.396186+01:00"
    },
    {
      "id": 9,
      "title": "Fysikalen Dag 9",
      "description": "9 dagen av Fysikalen.",
      "event_at": "2025-11-08T18:21:39.396186+01:00"
    },
    {
      "id": 10,
      "title": "Fysikalen Dag 10",
      "description": "10 dagen av Fysikalen.",
      "event_at": "2025-11-09T18:21:39.396186+01:00"
    },
    {
      "id": 11,
      "title": "Fysikalen Dag 11",
      "description": "11 dagen av Fysikalen.",
      "event_at": "2025-11-10T18:21:39.396186+01:00"
    },
    {
      "id": 12,
      "title": "Fysikalen Dag 12",
      "description": "12 dagen av Fysikalen.",
      "event_at": "2025-11-11T18:21:39.396186+01:00"
    },
    {
      "id": 13,
      "title": "Fysikalen Dag 13",
      "description": "13 dagen av Fysikalen.",
      "event_at": "2025-11-12T18:21:39.396186+01:00"
    },
    {
      "id": 14,
      "title": "Fysikalen Dag 14",
      "description": "14 dagen av Fysikalen.",
      "event_at": "2025-11-13T18:21:39.396186+01:00"
    },
    {
      "id": 15,
      "title": "Fysikalen Dag 15",
      "description": "15 dagen av Fysikalen.",
      "event_at": "2025-11-14T18:21:39.396186+01:00"
    },
    {
      "id": 16,
      "title": "Fysikalen Dag 16",
      "description": "16 dagen av Fysikalen.",
      "event_at": "2025-11-15T18:21:39.396186+01:00"
    },
    {
      "id": 17,
      "title": "Fysikalen Dag 17",
      "description": "17 dagen av Fysikalen.",
      "event_at": "2025-11-16T18:21:39.396186+01:00"
    },
    {
      "id": 18,
      "title": "Fysikalen Dag 18",
      "description": "18 dagen av Fysikalen.",
      "event_at": "2025-11-17T18:21:39.396186+01:00"
    },
    {
      "id": 19,
      "title": "Fysikalen Dag 19",
      "description": "19 dagen av Fysikalen.",
      "event_at": "2025-11-18T18:21:39.396186+01:00"
    },
    {
      "id": 20,
      "title": "Fysikalen Dag 20",
      "description": "20 dagen av Fysikalen.",
      "event_at": "2025-11-19T18:21:39.396186+01:00"
    }
    ],
    past: [
      { id: 3, name: "Past Event 1", date: "2024-11-01" },
      { id: 4, name: "Past Event 2", date: "2024-10-15" },
    ],
  };

  
  useEffect(() => {
    // Fetch events from the backend

    if(true){
      setUpcomingEvents(testData.upcoming);
      setPastEvents(testData.past);
    }
    else {
      axiosInstance.get('/events/').then((response) => {
        setUpcomingEvents(response.data.upcoming);
        setPastEvents(response.data.past);
      });
    }
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
        <Dropdown.Toggle variant="secondary" id="dropdown-basic" className="dropdown-toggle">
          {showPast ? 'Hide' : 'Show'} Past Events
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
