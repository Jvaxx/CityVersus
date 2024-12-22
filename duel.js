let intervalID;

function createGame(board) {
    // style
    const linkElement = document.createElement("link");
    linkElement.href = "./duel.css";
    linkElement.rel = "stylesheet";
    document.head.append(linkElement);

    // lobby
    const playersElement = document.createElement("div");
    playersElement.className = "players"
    for (let player = 1; player < 3; player++) {
        const playerElement = document.createElement("div");
        playerElement.className = "player";

        const playerNameElement = document.createElement("div");
        playerNameElement.className = "player_name";
        playerNameElement.innerText = "Joueur " + player;
        playerNameElement.dataset.playerNumber = player;

        const playerStatusElement = document.createElement("div");
        playerStatusElement.className = "player_status not_ready";
        playerStatusElement.innerText = "Pas prêt";
        playerStatusElement.dataset.statusNumber = player;

        const playerLifeElement = document.createElement("div");
        playerLifeElement.className = "player_life empty";
        playerLifeElement.dataset.playerNumber = player;

        playerElement.append(playerNameElement, playerStatusElement, playerLifeElement);
        playersElement.append(playerElement);
    }
    board.append(playersElement);

    // qcm wrapper
    const qcmElement = document.createElement("div");
    qcmElement.className = "qcm_wrapper";

    // round number
    const roundElement = document.createElement("div");
    roundElement.className = "round_number empty";
    qcmElement.append(roundElement);

    // question asked
    const questionElement = document.createElement("div");
    questionElement.className = "question";

    const questionTextElement = document.createElement("div");
    questionTextElement.className = "question_text";
    questionTextElement.innerText = "En attente des joueurs...";
    questionElement.append(questionTextElement);
    qcmElement.append(questionElement);

    // timer
    const timerElement = document.createElement("div");
    timerElement.className = "timer empty";
    qcmElement.append(timerElement);

    // propositions
    const propositionsElement = document.createElement("div");
    propositionsElement.className = "propositions";
    let i = 0;
    for (let col = 0; col < 2; col++){
        for (let row = 0; row < 2; row++){
            const propositionElement = document.createElement("div")
            propositionElement.className = "proposition empty";
            propositionElement.innerText = "Proposition";
            propositionElement.dataset.number = i;
            propositionElement.dataset.id = 0;
            propositionsElement.append(propositionElement)
            i++
        }
    }
    qcmElement.append(propositionsElement);

    // lobby ID
    const lobbyInfoElement = document.createElement("div");
    lobbyInfoElement.className = "lobby_info";
    const lobbyTextElement = document.createElement("div");
    lobbyTextElement.className = "lobby_text";
    lobbyTextElement.innerText = "Code du lobby: ";
    const lobbyIdElement = document.createElement("div");
    lobbyIdElement.className = "lobby_id";
    lobbyIdElement.innerText = "...";
    lobbyIdElement.addEventListener("click", () => {
        navigator.clipboard.writeText(lobbyIdElement.innerText);
        console.log("copié.");
    });
    lobbyInfoElement.append(lobbyTextElement, lobbyIdElement);
    qcmElement.append(lobbyInfoElement);

    // join a lobby
    const lobbyJoinElement = document.createElement("div");
    lobbyJoinElement.className = "lobby_join";
    const lobbyJoinCodeElement = document.createElement("input");
    lobbyJoinCodeElement.className = "lobby_join_input";
    lobbyJoinCodeElement.placeholder = "Rejoindre un lobby"
    const lobbyJoinButtonElement = document.createElement("button");
    lobbyJoinButtonElement.className = "action button lobby_join_button";
    lobbyJoinButtonElement.innerText = "Rejoindre";
    lobbyJoinButtonElement.addEventListener("click", () => {
        const inputElement = document.querySelector(".lobby_join_input");
        window.location.href = "?join=" + inputElement.value;
    });
    lobbyJoinElement.append(lobbyJoinCodeElement, lobbyJoinButtonElement);
    qcmElement.append(lobbyJoinElement);

    board.append(qcmElement);
}


function playRound(board, player, proposition_id) {
    if (player !== 1 && player !== 2) {
        throw new Error("Plays not valid");
    }
    const propositionElement = document.querySelector("[data-id='" + proposition_id +"']");
    if (propositionElement === undefined) {
        throw new Error("Proposition not found");
    }
    propositionElement.classList.add("selected");
}


function setReady(board, player) {
    const playerElement = document.querySelector("[data-status-number='" + player + "']");
    playerElement.classList.replace("not_ready", "ready");
    playerElement.innerText = "Prêt";
}


function initLobby(board, player_number) {
    const playerElement = board.querySelector(".player_name[data-player-number='" + player_number + "']");
    playerElement.classList.add("this_player");

    const readyElement = board.querySelector(".player_status[data-status-number='" + player_number + "']");
    readyElement.classList.add("this_player");
}


function initRound(board, question, propositions, players_life, round_number) {
    // timer reset
    clearInterval(intervalID);
    const timerElement = board.querySelector(".timer");
    timerElement.classList.add("empty");

    // hide ready state
    const statusElements = board.querySelectorAll(".player_status");
    statusElements.forEach((element) => element.classList.add("empty"));

    // update life indicators
    const playerLifeElements = board.querySelectorAll(".player_life");
    playerLifeElements.forEach((playerLifeElement) => {
        playerLifeElement.innerText = Math.round(players_life[playerLifeElement.dataset.playerNumber - 1]);
        playerLifeElement.classList.remove("empty");
    });

    // remove last damages
    const damageElements = board.querySelectorAll(".damage");
    damageElements.forEach((damageElement) => damageElement.remove());

    // update round element
    const roundElement = board.querySelector(".round_number");
    roundElement.classList.remove("empty");
    roundElement.innerText = "Round: " + round_number;

    // questions
    const questionElement = board.querySelector(".question_text");
    questionElement.classList.remove("empty");
    const propositionsElement = board.querySelectorAll(".proposition");
    questionElement.innerText = question;
    propositionsElement.forEach((propositionElement, i) => {
        propositionElement.innerText = propositions[i][0];
        propositionElement.dataset.id = propositions[i][1];
        propositionElement.classList.remove("empty");
        propositionElement.classList.remove("selected");
        propositionElement.classList.remove("correct");
    });
}


function endRound(board, correct_id, last_damages) {
    // timer reset
    clearInterval(intervalID);
    const timerElement = board.querySelector(".timer");
    timerElement.classList.add("empty");

    // show answer
    const correctElement = board.querySelector(".proposition[data-id='" + correct_id + "']");
    correctElement.classList.add("correct");

    // show last damages
    const playerLifeElements = board.querySelectorAll(".player_life");
    playerLifeElements.forEach((playerLifeElement, index) => {
        const damageElement = document.createElement("div");
        damageElement.className = "damage";
        damageElement.innerText = "-" + last_damages[index];
        damageElement.dataset.value = last_damages[index];
        playerLifeElement.insertAdjacentElement('afterend', damageElement);
    });
}


function endGame(board, winner, players_life) {
    // hide propositions
    const propositionsElements = board.querySelectorAll(".proposition");
    propositionsElements.forEach((element) => {
        element.classList.add("empty");
    });

    // hide question
    const questionElement = board.querySelector(".question");
    questionElement.classList.add("empty");

    // display winner
    const qcmWrapperElement = board.querySelector(".qcm_wrapper");
    const winnerElement = document.createElement("div");
    winnerElement.className = "winner";
    winnerElement.innerText = "Vainqueur: " + winner;
    const timerElement = board.querySelector(".timer");
    qcmWrapperElement.insertBefore(winnerElement, timerElement.nextSibling);

    // update life indicators
    const playerLifeElements = board.querySelectorAll(".player_life");
    playerLifeElements.forEach((playerLifeElement) => {
        playerLifeElement.innerText = Math.round(players_life[playerLifeElement.dataset.playerNumber - 1]);
        playerLifeElement.classList.remove("empty");
    });

}


function startTimer(board, countdown) {
    const timerElement = board.querySelector(".timer");
    timerElement.classList.remove("empty");
    timerElement.innerText = countdown;
    const propositions = board.querySelectorAll(".proposition");
    let answered = false;
    propositions.forEach((proposition) => {
        if (proposition.classList.contains("selected")) {
            answered = true;
        }
    })
    let time = countdown;
    intervalID = setInterval(() => {
        time -= 0.1;
        timerElement.innerText = "Temps restant: " + Math.round(time*100)/100;

        if (Math.round(time*100)/100 === 0.0 && !answered) {
            const propositionElement = board.querySelector("[data-number='" + 0 + "']");
            propositionElement.click();
        }
    }, 100);
}


export {createGame, playRound, initRound, setReady, startTimer, initLobby, endRound, endGame};