import Phaser from "phaser";
import {buildBaseWSMessage} from "../config/serverConfig.js";
import ErrorMessage from "../components/ErrorMessage.js";

export default class LobbyScene extends Phaser.Scene {
  constructor() {
    super("lobby-scene");
  }

  preload() {
    this.load.image("startGame", "/assets/start-game.png");
  }

  init(data) {
    this.playerName = data.playerName;
    this.playerId = data.playerId;
    this.gameId = data.gameId;
    this.isHost = data.isHost;
    this.hostId = data.hostId;
    this.players = { ...data.initialPlayers };

    this.ws = data.ws;
    this.ws.onopen = () => this.handleWebSocketOpen();
    this.ws.onmessage = (event) => this.handleWebSocketMessage(event);

    this.playersList = this.add
      .text(this.scale.width / 2, 180, "You", {
        fontSize: "20px",
        fill: "#c671ff",
        align: "center",
        wordWrap: { width: this.scale.width, useAdvancedWrap: true },
      })
      .setOrigin(0.5);
  }

  create() {
    this.createText(`Lobby ${this.gameId}`, 50, "30px", "bold");
    this.createText(`Welcome \n${this.playerName}!`, 100, "22px");
    this.createText("Players:", 160, "24px", "bold");

    this.isHost
      ? this.createStartButton()
      : this.createText(
          "Waiting for host\nto start game...",
          this.scale.height - 50,
          "24px",
        );

    this.errorMessage = new ErrorMessage(
      this,
      this.scale.width / 2,
      40,
      this.scale.width * 0.9,
    );

    this.updatePlayersList(this.players, this.hostId);
  }

  createText(text, y, fontSize, fontStyle = "") {
    return this.add
      .text(this.scale.width / 2, y, text, {
        fontSize,
        fill: "#c671ff",
        fontStyle,
        align: "center",
      })
      .setOrigin(0.5);
  }

  createStartButton() {
    this.createButton("startGame", this.scale.height - 50, () => {
      this.scene.start("scene-game", {
        websocket: this.ws,
        playerId: this.playerId,
        gameId: this.gameId,
        isHost: true,
      });
    });
  }

  createButton(key, y, callback) {
    this.add
      .image(this.scale.width / 2, y, key)
      .setInteractive()
      .on("pointerdown", callback)
      .setOrigin(0.5);
  }

  updatePlayersList(players, hostId) {
    const playerNames = Object.entries(players).map(([id, player]) => {
      let displayName = player === this.playerName ? "You" : player;
      if (id === hostId) {
        displayName += " ⭐";
      }
      return displayName;
    });

    this.playersList
      .setText(playerNames.join("\n"))
      .setOrigin(0.5, 0)
      .setY(180);
  }

  handlePlayerJoin(playerId, playerName) {
    this.players[playerId] = playerName;
    this.updatePlayersList(this.players, this.hostId);
  }

  handlePlayerDisconnect(playerId) {
    delete this.players[playerId];
    this.updatePlayersList(this.players, this.hostId);
  }

  handleWebSocketOpen() {
    this.sendMessage("join", { player_name: this.playerName });
  }

  handleWebSocketMessage(event) {
    const message = JSON.parse(event.data);

    if (message.method === "ping") {
      this.sendMessage("pong", {});
    } else if (message.method === "join") {
      this.handlePlayerJoin(message.playerId, message.playerName);
    } else if (message.method === "disconnect") {
      this.handlePlayerDisconnect(message.playerId);
    }
  }

  sendMessage(method, payload) {
    const message = buildBaseWSMessage(this.playerId, this.gameId);
    message.method = method;
    message.payload = payload;
    this.ws.send(JSON.stringify(message));
  }
}
