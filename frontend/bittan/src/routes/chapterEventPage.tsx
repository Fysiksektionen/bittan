import { useParams } from 'react-router-dom';
import { useLocation } from 'react-router-dom'
import { ChapterEvent } from '../types';
import { useEffect, useState } from 'react';

export default function ChapterEventPage() {
	const { chapterEventId } = useParams();
	const location = useLocation();
	
	const [chapterEvent, setChapterEvent] = useState<null|ChapterEvent>(location.state === null ? null : location.state.chapterEvent);
	
	return (
		<div>
      		Welcome to the Chapter Event page for event id {chapterEventId}.
			{chapterEvent === null ? `We have null` : `We have CE`}
	  	</div>
	)
}