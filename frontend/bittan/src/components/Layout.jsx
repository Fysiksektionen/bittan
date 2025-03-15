import React from 'react';
import { Navbar, Container, Nav } from 'react-bootstrap';
import Footer from "./Footer.jsx"

const basename = process.env.PUBLIC_URL || "/";

const Layout = ({ children }) => (
  <div className='d-flex flex-column min-vh-100'>
    <Navbar bg="light" expand="lg">
      <Container>
        <Navbar.Brand href={basename}>Biljettbokning</Navbar.Brand>
        <Nav className="me-auto">
          <Nav.Link href="/">Fysikalen</Nav.Link>
        </Nav>
      </Container>
    </Navbar>
    <Container className='flex-grow-1 py-5'>{children}</Container>
    <Footer></Footer>
  </div>
);

export default Layout;
