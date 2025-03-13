import { Col, Container, Row } from "react-bootstrap";


function Footer(){
	return(
		<footer className="bg-light py-1">
			<Container>
				<Row className="py-1 align-items-start">
					<Col className="text-left">
							Kontakt:{' '}
							<a href="mailto:biljettsupport@f.kth.se" className="text-dark">
								biljettsupport@f.kth.se
							</a>
					</Col>
				</Row>
				<Row className="align-items-start py-1">
					<Col>
						Postaddress: <br/>
						Fysiksektionen, THS, <br/> 
						100 44 Stockholm 
					</Col>
				</Row>
				<Row className="pt-4 pb-1">
					<Col className="text-left mb-0">
						<small>&copy; {new Date().getFullYear()} Fysiksektionen, organisationsnummer 802411-8948</small>
					</Col>
				</Row>
			</Container>
		</footer>
	)
}

export default Footer;
