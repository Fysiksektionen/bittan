import { Link } from "react-router-dom";

export default function Root() {
	return (
		<div>
		  Hello this is my homescreen.
		  <Link to={`otherpage`}>Go to some other page</Link>
		</div>
	  );
}