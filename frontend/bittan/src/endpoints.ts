import axios from "axios";
import { ChapterEvent } from "./types";
  
  export async function getChapterEvents(): Promise<ChapterEvent[]> {
	const response = await axios.get<ChapterEvent[]>('http://localhost:8000/get_chapterevents/');
	return response.data;
  }
