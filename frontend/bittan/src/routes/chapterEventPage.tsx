import { useParams } from 'react-router-dom';
export default function ChapterEventPage() {
	var { chapterEventId } = useParams();

	return (
		<div>
      		Welcome to the Chapter Event page for event id {chapterEventId}.
	  	</div>
	)
}