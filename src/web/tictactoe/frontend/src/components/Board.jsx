// src/components/Board.jsx
import React, { useState, useEffect } from 'react';
import './Board.css';
import { hourglass } from 'ldrs'



const GAME_STATES = {
	X_TURN: 'CURRENT PLAYER X',
	O_TURN: 'CURRENT PLAYER O',
	X_WON: 'PLAYER X WON',
	O_WON: 'PLAYER O WON',
	DRAW: 'DRAW',
};

const Board = () => {

	const [squares, set_squares] = useState(Array(9).fill(null));
	const [is_x_next, set_is_next] = useState(true);
	const [ws, set_ws] = useState(null);
	const [game_state, set_game_state] = useState(GAME_STATES.X_TURN);

	// This is set when the player clicks on a square
	// and is reset when the server sends an ACK, so when we receive a message "ACK"
	const [is_waiting, set_is_waiting] = useState(false);

	useEffect(() => {
		const websocket = new WebSocket('ws://localhost:6789');
		set_ws(websocket);

		websocket.onmessage = (event) => {
			// If the message contains an 'ACK'
			console.log("DEBUG event.data: ", event.data)
			if (event.data === 'ACK') {
				console.log("Received ACK");
				set_is_waiting(false);
				return;
			}
			console.log("Received message: ", event.data);
		};
		
		websocket.onopen = () => {
			console.log("Websocket connected");
		}

		websocket.onclose = () => {
			console.log("Websocket disconnected");
		}

		return () => {
			websocket.close();
		};
	}, []);

	hourglass.register()



	const handle_click = (index) => {

		// If waiting for ACK
		if (is_waiting === true) {
			console.log("Waiting for ACK");
			return;
		}

		// If game already finished
		if(game_state !== GAME_STATES.X_TURN && game_state !== GAME_STATES.O_TURN){
			console.log("Player %s already won !!", game_state === GAME_STATES.X_WON ? "X" : "O");
			return;
		}
		else if (squares[index])
		{
			console.log("Square already filled !!");
			return;
		}
		else {
			set_is_waiting(true);
		}


		const new_squares = squares.slice();
		new_squares[index] = is_x_next ? 'X' : 'O';
		set_squares(new_squares);

		// Compute game state
		
		set_is_next(!is_x_next);
		let local_game_state = compute_game_state(new_squares);
		
		if (local_game_state === null)
			set_game_state(is_x_next ? GAME_STATES.O_TURN : GAME_STATES.X_TURN);
		else
			set_game_state(local_game_state);

		console.log("Current Game state: ", game_state);

		
		if (ws) {
			// Send click action and game state
			ws.send(JSON.stringify({ action: 'click', game_state: game_state, index: index, squares: new_squares }));
			console.log(game_state);
		}
	};

	const reset = () => {
		if (ws) {
			ws.send(JSON.stringify({ action: 'reset' }));
		}
		set_squares(Array(9).fill(null));
		set_is_next(true);

		set_game_state(GAME_STATES.X_TURN);
		set_is_waiting(false);
	}



	// This function computes the game state
	// Returns the winner if any, full board if draw, null otherwise
	const compute_game_state = (squares) => {
		const lines = [
			[0, 1, 2],
			[3, 4, 5],
			[6, 7, 8],
			[0, 3, 6],
			[1, 4, 7],
			[2, 5, 8],
			[0, 4, 8],
			[2, 4, 6],
		];
		
		for (let i = 0; i < lines.length; i++) {
			const [a, b, c] = lines[i];
		
			if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
				const state = squares[a] === 'X' ? GAME_STATES.X_WON : GAME_STATES.O_WON;
				return state;
			}
		}
		
		if (squares.every((square) => square !== null)) {
			return GAME_STATES.DRAW;
		}
		
		return null;
	};

	let status;    

	const result = compute_game_state(squares);
	
	// There is a winner or draw
	if (result) {
		status = result;
	}
	else { // No winner or draw
		status = game_state;
	}

	if (is_waiting) {
		status = "Waiting for move on the board...";
	}
	
	// return with the hourglass if waiting for ACK
	if (is_waiting) {
		return (
			<div>
				<div className="status">{status}

					<l-hourglass
						size="35"
						bg-opacity="0.1"
						speed="1.75"
						color="white"
					></l-hourglass>

				</div>
				<div className="board-row">
					{render_square(0)}
					{render_square(1)}
					{render_square(2)}
				</div>
				<div className="board-row">
					{render_square(3)}
					{render_square(4)}
					{render_square(5)}
				</div>
				<div className="board-row">
					{render_square(6)}
					{render_square(7)}
					{render_square(8)}
				</div>
				<div>
					<button className="resetButton" onClick={reset}>RESET GAME</button>
				</div>
			</div>
		);
	}
	else
	{
		return (
			<div>
				<div className="status">{status}</div>
				<div className="board-row">
					{render_square(0)}
					{render_square(1)}
					{render_square(2)}
				</div>
				<div className="board-row">
					{render_square(3)}
					{render_square(4)}
					{render_square(5)}
				</div>
				<div className="board-row">
					{render_square(6)}
					{render_square(7)}
					{render_square(8)}
				</div>
				<div>
					<button className="resetButton" onClick={reset}>RESET GAME</button>
				</div>
			</div>
		);
	}

	function render_square(i)
	{
		return (
			<button className="square" onClick={() => handle_click(i)}>
				{squares[i]}
			</button>
		);
	}
};

export default Board;
