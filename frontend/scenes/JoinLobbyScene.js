import Phaser from "phaser";
import { server } from "../config/serverConfig.js";
import ErrorMessage from "../components/ErrorMessage.js";

export default class JoinLobbyScene extends Phaser.Scene {
  constructor() {
    super("join-lobby-scene");
  }

  preload() {
    this.load.image("joinLobby", "/assets/join-lobby.png");
    this.load.image("refresh", "/assets/refresh.png");
  }

  init(data) {
    this.playerName = data.playerName;
    this.ws = data.ws; // Assume WebSocket is passed from previous scene
  }

  create() {
    this.createText("Select a lobby:", 50, "28px");
    this.createLoadingMessage();
    this.createRefreshButton();

    this.errorMessage = new ErrorMessage(
      this,
      this.scale.width / 2,
      this.scale.height / 2,
      this.scale.width * 0.9
    );

    this.fetchLobbies();
  }

  createText(text, y, fontSize) {
    return this.add
      .text(this.scale.width / 2, y, text, {
        fontSize,
        fill: "#c671ff",
        fontStyle: "bold",
        align: "center",
      })
      .setOrigin(0.5);
  }

  createLoadingMessage() {
    this.lobbiesLoadingMessage = this.createText(
      "Loading lobbies...",
      this.scale.height / 2,
      "24px"
    );
    this.lobbiesContainer = this.add.container(this.scale.width / 2, 100);
  }

  createRefreshButton() {
    this.refreshButton = this.add
      .image(this.scale.width / 2, this.scale.height - 50, "refresh")
      .setInteractive()
      .on("pointerdown", () => this.fetchLobbies())
      .setOrigin(0.5);
  }

updateLobbiesList(lobbies) {
  this.lobbiesContainer.removeAll(true);
  this.lobbiesLoadingMessage.setText(
    lobbies.length === 0 ? "No lobbies found" : ""
  );

  lobbies.slice(0, 5).forEach((lobbyCode, index) => {
    const button = this.createLobbyButton(lobbyCode, index * 60);
    this.lobbiesContainer.add(button);
  });
}

  createLobbyButton(lobbyCode, y) {
    return this.add
      .text(0, y, lobbyCode, {
        fontSize: "30px",
        fill: "#fff",
        backgroundColor: "#c671ff",
        padding: { x: 10, y: 5 },
      })
      .setInteractive()
      .on("pointerdown", () => this.joinLobby(lobbyCode, this.playerName))
      .setOrigin(0.5);
  }

  fetchLobbies() {
    fetch(`${server.api()}/lobbies`)
      .then((response) => {
        console.log(response)
        if (!response.ok) {
          return response.json().then((data) => {
            throw new Error(data.error || "Failed to fetch lobbies");
          });
        }
        return response.json();
      })
      .then((data) => {
        this.updateLobbiesList(data);
      })
      .catch((error) => {
        console.error("Error fetching lobbies:", error);
        this.errorMessage.show(error.message);
      });
  }

  joinLobby(lobbyCode, playerName) {
    const message = {
      method: "join",
      player_id: null,
      payload: {
        player_name: playerName,
        lobby_code: lobbyCode,
      },
    };

    this.ws.send(JSON.stringify(message));

    this.ws.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.error) {
        this.errorMessage.show(response.error || "Failed to join lobby");
        console.error("Error joining lobby:", response.error);
      } else {
        this.scene.start("lobby-scene", {
          playerName,
          playerId: response.playerId,
          lobbyCode,
          isHost: false,
          initialPlayers: response.lobby.players,
          hostId: response.lobby.host_id,
        });
      }
    };
  }
}

