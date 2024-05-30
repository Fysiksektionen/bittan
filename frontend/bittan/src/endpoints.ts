import axios from "axios";
import { ChapterEvent } from "./types";
  
export async function getChapterEvents(): Promise<ChapterEvent[]> {
	const response = await axios.get<any[]>('http://localhost:8000/get_chapterevents/');
	return response.data.map(ce => {return {...ce, event_at: new Date(ce.event_at)}});
}

export async function getChapterEventById(chapterEventId: number): Promise<ChapterEvent> {
	const response = await axios.get<any>('http://localhost:8000/get_chapterevent_by_id/', {params: {"id": chapterEventId}});
	const ce = response.data;
	return {...ce, event_at: new Date(ce.event_at)};
}
