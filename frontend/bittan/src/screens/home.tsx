import React from 'react';

function testOnClick() {
	console.log("Click!")
}

export default function HomeScreen() {
  return (
    <div>
      Hello this is my homescreen.
	  <button onClick={testOnClick}>Click here to go to other screen.</button>
    </div>
  );
}

