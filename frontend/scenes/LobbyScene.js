import Phaser from "phaser";
import { api } from "../config/serverConfig.js";
import ErrorMessage from "../components/ErrorMessage.js";
import axios from 'axios';

export default class LobbyScene extends Phaser.Scene {
  constructor() {
    super("lobby-scene");
  }

  preload() {
    this.load.image("startGame", "/assets/start-game.png");
  }

  init(data) {
    this.playerName = data.playerName;
    this.lobbyCode = data.lobbyCode;
    this.isHost = data.isHost;
  }

  create() {
    this.createText(`Lobby ${this.lobbyCode}`, 50, "30px", "bold");
    this.createText(`Welcome \n${this.playerName}!`, 100, "22px");
    this.createText("Players:", 160, "24px", "bold");

    this.playersList = this.add
      .text(this.scale.width / 2, 180, "You", {
        fontSize: "20px",
        fill: "#c671ff",
        align: "center",
        wordWrap: { width: this.scale.width, useAdvancedWrap: true },
      })
      .setOrigin(0.5);

    if (this.isHost) {
      this.startButton = this.createButton(
        "startGame",
        this.scale.height - 50,
        () => {
          this.startGame();
        },
      );
    } else {
      this.createText(
        "Waiting for host\nto start game...",
        this.scale.height - 50,
        "24px",
      );
    }

    this.errorMessage = new ErrorMessage(
      this,
      this.scale.width / 2,
      40,
      this.scale.width * 0.9,
    );

    this.fetchPlayersList();
    this.time.addEvent({
      delay: 1000,
      callback: () => this.fetchPlayersList(),
      callbackScope: this,
      loop: true,
    });
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

  createButton(key, y, callback) {
    return this.add
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

  startGame() {
    // axios.post(`${api.host()}/start`, {
    //   nbPlayers: this.playersList.length,
    // }).then((response) => {
    //   console.log(response.data);
    // }).catch((error) => {
    //     console.error("Error starting the game:", error.response ? error.response.data : error.message);
    //   });
    this.scene.start("scene-game");
  }

  fetchPlayersList() {
    fetch(`${api.host()}/lobbies/${this.lobbyCode}`)
      .then((response) => {
        if (!response.ok) {
          return response.json().then((data) => {
            throw new Error(data.error || "Failed to fetch player list");
          });
        }
        return response.json();
      })
      .then((data) => {
        this.updatePlayersList(data.players, data.host_id);
      })
      .catch((error) => {
        console.error("Error fetching player list:", error);
        this.errorMessage.show(error.message || "Failed to fetch player list");
      });
  }
}

