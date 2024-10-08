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
    this.playerName = this.generateRandomName();

    this.add
      .image(this.scale.width / 2, this.scale.height / 2 + 115, "createLobby")
      .setInteractive()
      .on("pointerdown", () => this.createLobby(this.playerName));

    this.add
      .image(this.scale.width / 2, this.scale.height - 50, "joinLobby")
      .setInteractive()
      .on("pointerdown", () => this.joinLobby(this.playerName));

    this.errorMessage = new ErrorMessage(
      this,
      this.scale.width / 2,
      this.scale.height / 2,
      this.scale.width * 0.9
    );
  }

  createLobby(playerName) {
    const ws = new WebSocket(server.websocket());
    
    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onopen = () => {
      const createMessage = this.buildCreateWSMessage(playerName);
      ws.send(JSON.stringify(createMessage));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.error) {
        this.errorMessage.show(data.error);
        return;
      }

      const playerId = data.player_id;
      const gameId = data.game_id;

      const players = data.lobby.players;
      const mappedPlayers = Object.entries(players).reduce((acc, [id, player]) => {
          acc[id] = player.name;
          return acc;
      }, {});

      this.scene.start("lobby-scene", {
        playerName,
        playerId,
        gameId,
        isHost: true,
        initialPlayers: mappedPlayers,
        hostId: data.lobby.host_id,
        ws: ws,
      });
    };
  }

  joinLobby(playerName) {
    this.scene.start("join-lobby-scene", { playerName });
  }

  buildCreateWSMessage(playerName) {
    const message = buildBaseWSMessage(null, null);
    message.method = "create";
    message.payload = {
      host_name: playerName,
    };
    return message;
  }
}

