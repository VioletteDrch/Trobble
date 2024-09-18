import Phaser from "phaser";
import {api} from "../config/serverConfig.js";

export default class CreateLobbyScene extends Phaser.Scene {
  constructor() {
    super("create-lobby-scene");
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
    this.cameras.main.setBackgroundColor("#FFFFC0");

    this.lobbyCodeText = this.add.text(this.scale.width / 2, 50, `Lobby ${this.lobbyCode}`, {
      fontSize: '30px',
      fontStyle: 'bold',
      align: 'center',
      fill: '#c671ff',
    }).setOrigin(0.5);

    this.playersLabel = this.add.text(this.scale.width / 2, 100, `Welcome \n${this.playerName}!`, {
      fontSize: '22px',
      fill: '#c671ff',
      align: 'center'
    }).setOrigin(0.5);

    this.playersLabel = this.add.text(this.scale.width / 2, 160, "Players:", {
      fontSize: '24px',
      fill: '#c671ff',
      fontStyle: 'bold',
      align: 'center'
    }).setOrigin(0.5);

    this.playersList = this.add.text(this.scale.width / 2, 180, "You", {
      fontSize: '22px',
      fill: '#c671ff',
      align: 'center'
    }).setOrigin(0.5);

    if (this.isHost) {
      this.startButton = this.add.image(this.scale.width / 2, this.scale.height - 50, "startGame")
        .setInteractive()
        .on("pointerdown", () => {
          this.scene.start('scene-game');
        });
    } else {
      this.loadingText = this.add.text(this.scale.width / 2, this.scale.height - 50, "Waiting for host\nto start game...",
        {
          fontSize: '24px',
          fill: '#c671ff',
        }
      ).setOrigin(0.5);
    }

    this.fetchPlayersList();

    this.time.addEvent({
      delay: 1000,
      callback: this.fetchPlayersList,
      callbackScope: this,
      loop: true,
    });
  }

  fetchPlayersList() {
    fetch(`${api.host()}/lobbies/${this.lobbyCode}`)
      .then(response => response.json())
      .then(data => {
        this.updatePlayersList(data.players);
      })
      .catch(error => {
        console.error("Error fetching lobby info:", error);
      });
  }

  updatePlayersList(players) {
    const playerNames = Object.values(players).map(player => {
      return player === this.playerName ? `You` : player;
    });
    this.playersList.setText(playerNames.join('\n')).setOrigin(0.5, 0).setY(180);
  }}

