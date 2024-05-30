import React from "react";
import { Link } from "react-router-dom";
import { useEffect, useState } from 'react';
import { getChapterEvents } from "../endpoints";
import { ChapterEvent } from "../types";
import { AxiosError } from "axios";

export default function Root() {
	const [chapterEvents, setChapterEvents] = useState<ChapterEvent[]>([]);
	const [fetchingChapterEvents, setFetchingChapterEvents] = useState(true);
	const [fetchChapterEventsFailed, setFetchChapterEventsFailed] = useState(false);
	useEffect(() => {
		const loadChapterEvents = async () => {
			setFetchingChapterEvents(true);
			var recievedChapterEvents: ChapterEvent[] = [];
			try {
				recievedChapterEvents = await getChapterEvents();
			} catch (err) {
				if (err instanceof AxiosError) {
					setFetchingChapterEvents(false);
					setFetchChapterEventsFailed(true);
				} else {
					throw err;
				}
				return;
			}
			setChapterEvents(recievedChapterEvents)
			setFetchingChapterEvents(false);
			setFetchChapterEventsFailed(false);
		}
		loadChapterEvents();
	}, []);
	
	function chapterEventComponents(): React.JSX.Element[] {
		return chapterEvents.map(ce => <li key={ce.id}><Link to={"events/" + ce.id}>{ce.title}</Link></li>);
	}
	return (
		<div>
		  Hello this is my homescreen.
		  <Link to={`otherpage`}>Go to some other page</Link>
		  {fetchingChapterEvents ? <>Hämtar data...</> : <>Datan är hämtad!</>}
		  {fetchChapterEventsFailed ? <>Failade att hämta data.</> : <></>}
		  {chapterEventComponents()}
		</div>
	  );
}