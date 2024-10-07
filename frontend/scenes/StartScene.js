import Phaser from "phaser";
import { server, buildBaseWSMessage } from "../config/serverConfig.js";
import ErrorMessage from "../components/ErrorMessage.js";

export default class StartScene extends Phaser.Scene {
  constructor() {
    super("scene-start");
  }

  preload() {
    this.load.image("createLobby", "/assets/create-lobby.png");
    this.load.image("joinLobby", "/assets/join-lobby.png");
    this.load.image("logo", "/assets/logo.png");
  }

  generateRandomName() {
    const objects = [
      "Frikadeller",
      "Smørrebrød",
      "KimLarsen",
      "Pølse",
      "Kage",
      "Lakrids",
      "AndersAnd",
      "SkagenSild",
      "Lego",
      "Dørhåndtag",
      "Klovn",
    ];

    const titles = [
      "Konge",
      "Dronning",
      "Entusiast",
      "Mester",
      "Lord",
      "Ekspert",
      "Junkie",
    ];

    const word1 = objects[Math.floor(Math.random() * objects.length)];
    const word2 = titles[Math.floor(Math.random() * titles.length)];
    const number = Math.floor(Math.random() * 99) + 1;

    return `${word1}${word2}${number}`;
  }

  create() {
    this.logo = this.add.image(160, 160, "logo").setScale(0.3);

    this.userName = this.generateRandomName();

    this.add
      .image(this.scale.width / 2, this.scale.height / 2 + 115, "createLobby")
      .setInteractive()
      .on("pointerdown", () => this.createLobby(this.userName));

    this.add
      .image(this.scale.width / 2, this.scale.height - 50, "joinLobby")
      .setInteractive()
      .on("pointerdown", () => this.joinLobby(this.userName));

    this.errorMessage = new ErrorMessage(
      this,
      this.scale.width / 2,
      this.scale.height / 2,
      this.scale.width * 0.9
    );
  }

  createLobby(playerName) {
    fetch(`${server.api()}/lobbies`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        host_name: playerName,
        private: false,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((data) => {
            throw new Error(data.error || "Failed to create lobby");
          });
        }
        return response.json();
      })
      .then((data) => {
        const ws = new WebSocket(server.websocket());
        const playerId = data.user_id;
        ws.onerror = (error) => {
          console.error("ws error", error);
        };
        ws.onopen = (ev) => {
          ws.send(
            JSON.stringify(this.buildCreateWSMessage(playerId, data.lobby_code))
          );
          this.scene.start("lobby-scene", {
            playerName,
            playerId,
            lobbyCode: data.lobby_code,
            isHost: true,
            initialPlayers: data.lobby.players,
            hostId: data.lobby.host_id,
            ws: ws,
          });
        };
      })
      .catch((error) => {
        console.error("Error creating lobby:", error);
        this.errorMessage.show(error.message || "Failed to create lobby");
      });
  }

  joinLobby(playerName) {
    this.scene.start("join-lobby-scene", { playerName });
  }

  buildCreateWSMessage(playerId, gameId) {
    const message = buildBaseWSMessage(playerId, gameId);
    message.method = "create";
    return message;
  }
}
