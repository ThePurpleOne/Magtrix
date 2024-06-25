import { Chessground } from 'chessground'
import './node_modules/chessground/assets/chessground.base.css'
import './node_modules/chessground/assets/chessground.brown.css'
import './node_modules/chessground/assets/chessground.cburnett.css'

import { Chess } from 'chess.js';

//const Chess = require("chess.js");



const chess = new Chess();
const board = Chessground(document.querySelector('#board'), {
	orientation: 'white',
//---
	movable: {
		free: true, // Allow any piece to be moved
		color: 'white', // Allow both white and black to move
		events: {
			after: (orig, dest) => {
				chess.move({ from: orig, to: dest });
				console.log(chess.fen());
				board.set({ fen: chess.fen() });
			},
		},
	},
//---
	highlight: {
		lastMove: true,
		check: true,
		dragOver: true,
	},
//---
	animation: {
		enabled: true,
		duration: 200,
	},
//---
	premovable: {
		enabled: true,
		showDests : true,
		mark: 'premoves',
	},
//---
	draggable: {
		enabled: true,
		showGhost: true,
	},
//---
	drawable: {
		enabled: true,
	},

	events: {
		change : function() {
			console.log('change event')
		},

		move: (orig, dest, capturedPiece) => {
			console.log('move event')
		},

		select: (key) => {
			console.log('select event')
		},
	},
});
