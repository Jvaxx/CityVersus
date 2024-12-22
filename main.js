import {createGame, endGame, endRound, initLobby, initRound, playRound, setReady, startTimer} from "./duel.js";

let player_number = 0;
let answer_open = false;

window.addEventListener("DOMContentLoaded", () => {
    const board = document.querySelector(".board");
    console.log("coucou")
    createGame(board);
    const websocket = new WebSocket("ws://192.168.0.100:8001");

    init_game(websocket);
    receive_round(websocket, board);
    sendAnswer(websocket, board);

})


function init_game(websocket) {
    websocket.addEventListener("open", () => {
        const params = new URLSearchParams(window.location.search);
        let event = {"type": "init"};
        if (params.has("join")) {
            event.join = params.get("join");
            player_number = 2;
        } else {
            player_number = 1;
        }
        websocket.send(JSON.stringify(event));

    })
}


function sendAnswer(websocket, board) {
    board.addEventListener("click", ({target}) => {
        const answer_id = target.dataset.id;
        if (answer_id === undefined || !answer_open) {
            return;
        }
        playRound(board, player_number, answer_id);
        answer_open = false;
        const message = {"type": "answer", "geoname_id": answer_id};
        websocket.send(JSON.stringify(message));
    })
}


function receive_round(websocket, board) {
    websocket.addEventListener("message", ({data}) => {
        const message = JSON.parse(data);
        console.log(message);
        switch (message.type) {
            case "init":
                document.querySelector(".lobby_id").innerText = message.join;
                initLobby(board, player_number);

                const statusElement = document.querySelector(".player_status.this_player");
                statusElement.addEventListener("click", () => {
                    console.log("click sur ready.")
                    websocket.send(JSON.stringify({"type": "ready"}));
                });
                break;
            case "ready":
                setReady(board, message.player);
                break;
            case "round_start":
                initRound(board, message.question, message.propositions, message.players_life, message.round_number);
                answer_open = true;
                break;
            case "answer":
                startTimer(board, message.countdown);
                break;
            case "round_end":
                endRound(board, message.correct_id, message.last_damages);
                answer_open = false;
                break;
            case "game_end":
                endGame(board, message.winner, message.players_life);
                break;
            default:
                break;
        }
    })
}