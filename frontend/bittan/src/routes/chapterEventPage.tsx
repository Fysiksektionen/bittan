import { useParams } from 'react-router-dom';
import { useLocation } from 'react-router-dom'
import { ChapterEvent } from '../types';
import { useEffect, useState } from 'react';
import { getChapterEventById } from '../endpoints';
import { AxiosError } from "axios";

export default function ChapterEventPage() {
	const location = useLocation();
	const [chapterEventId, setChapterEventId] = useState(useParams().chapterEventId as unknown as number);
	const [chapterEvent, setChapterEvent] = useState<null|ChapterEvent>(location.state === null ? null : location.state.chapterEvent);
	
	useEffect(() => {
		if (chapterEvent !== null) {
			return;
		}
		const loadChapterEvent = async () => {
			var recievedChapterEvent: null|ChapterEvent = null;
			try {
				recievedChapterEvent = await getChapterEventById(chapterEventId);
			} catch (err) {
				if (err instanceof AxiosError) {
					// pass
				} else {
					throw err;
				}
				return;
			}
			setChapterEvent(recievedChapterEvent)
		}
		loadChapterEvent();
	}, [chapterEventId, chapterEvent]);

	return (
		<div>
      		Welcome to the Chapter Event page for event id {chapterEventId}.
			{chapterEvent === null ? `We have null` : `We have CE`}
	  	</div>
	)
}