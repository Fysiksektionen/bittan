import axios from "axios";
import { ChapterEvent } from "./types";
  
  export async function getChapterEvents(): Promise<ChapterEvent[]> {
	console.log("Gonna ask for chapter events")
	const response = await axios.get<ChapterEvent[]>('http://localhost:8000/get_chapterevents/');
	return response.data;
  }
