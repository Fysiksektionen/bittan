import React from 'react';
import { Navbar, Container, Nav } from 'react-bootstrap';

const Layout = ({ children }) => (
  <>
    <Navbar bg="light" expand="lg">
      <Container>
        <Navbar.Brand href="/">Event Booking</Navbar.Brand>
        <Nav className="me-auto">
          <Nav.Link href="/">Home</Nav.Link>
          <Nav.Link href="/events">Events</Nav.Link>
        </Nav>
      </Container>
    </Navbar>
    <Container>{children}</Container>
  </>
);

export default Layout;
