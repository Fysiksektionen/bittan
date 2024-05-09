import { Link } from "react-router-dom";
import { useEffect, useState } from 'react';
import { getChapterEvents } from "../endpoints";
import { ChapterEvent } from "../types";

export default function Root() {
	const [chapterEvents, setChapterEvents] = useState<ChapterEvent[]>([]);
	const [fetchingChapterEvents, setFetchingChapterEvents] = useState(true);
	useEffect(() => {
		const loadChapterEvents = async () => {
			try {
				setFetchingChapterEvents(true);
				const recievedChapterEvents = await getChapterEvents();
				setChapterEvents(recievedChapterEvents)
				setFetchingChapterEvents(false);
			} catch (error) {
				setFetchingChapterEvents(false); // TODO actually handle this in some way
				console.error(error);
			}
		}
		loadChapterEvents();
	}, []);
	
	function chapterEventComponents(): any[] {
		return chapterEvents.map(ce => <li>{ce.title}</li>);
	}
	return (
		<div>
		  Hello this is my homescreen.
		  <Link to={`otherpage`}>Go to some other page</Link>
		  {fetchingChapterEvents ? <>Hämtar data...</> : <>Datan är hämtad!</>}
		  {chapterEventComponents()}
		</div>
	  );
}