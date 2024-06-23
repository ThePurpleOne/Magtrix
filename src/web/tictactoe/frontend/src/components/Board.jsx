// src/components/Board.jsx
import React, { useState, useEffect } from 'react';
import './Board.css';

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
	const [ws, setWs] = useState(null);

	const [game_state, setGameState] = useState(GAME_STATES.X_TURN);


	useEffect(() => {
        const websocket = new WebSocket('ws://localhost:6789');
        setWs(websocket);

        websocket.onmessage = (event) => {
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


	const handle_click = (index) => {
		
		if (game_state !== GAME_STATES.X_TURN && game_state !== GAME_STATES.O_TURN) {
			console.log("Game over !!");
			setGameState(compute_game_state(squares));
			return;
		}
		else if (squares[index])
		{
			console.log("Square already filled !!");
			setGameState(compute_game_state(squares));
			return;
		}

		if (ws) {
			// Send click action and game state
			ws.send(JSON.stringify({ action: 'click', game_state: game_state, index: index }));
			console.log(game_state);
			// Print type of GAME_STATES
			console.log(typeof GAME_STATES);
		}

        const new_squares = squares.slice();
		new_squares[index] = is_x_next ? 'X' : 'O';
		
        set_squares(new_squares);
		set_is_next(!is_x_next);
		
		setGameState(is_x_next ? GAME_STATES.O_TURN : GAME_STATES.X_TURN);
	};

	const reset = () => {
		if (ws) {
			ws.send(JSON.stringify({ action: 'reset' }));
		}
		set_squares(Array(9).fill(null));
		set_is_next(true);

		setGameState(GAME_STATES.X_TURN);
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
	if (result) {
		status = result;
	}
	else {
		status = game_state;
	}

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
