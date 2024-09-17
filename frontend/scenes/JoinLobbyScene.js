import Phaser from "phaser";

export default class JoinLobbyScene extends Phaser.Scene {
  constructor() {
    super("join-lobby-scene");
  }

  preload() {
    this.load.image("joinLobby", "/assets/join-lobby.png");
  }

  init(data) {
    this.playerName = data.playerName;
  }

  create() {
    this.cameras.main.setBackgroundColor("#FFFFC0");

    this.nameText = this.add.text(this.scale.width / 2, this.scale.height / 2 - 50, "Enter lobby code:\n", {
      fontSize: '26px',
      fill: '#c671ff',
      fontStyle: 'bold',
      align: 'center'
    }).setOrigin(0.5);

    this.lobbyCode = "";

    this.input.keyboard.on('keydown', (event) => {
      if (event.keyCode === 8 && this.lobbyCode.length > 0) {
        this.lobbyCode = this.lobbyCode.slice(0, -1);
      } else if (event.key.length === 1 && this.lobbyCode.length < 7) {
        this.lobbyCode += event.key;
      }
      this.nameText.setText(`Enter lobby code:\n${this.lobbyCode}`);
    });

    this.add.image(this.scale.width / 2, this.scale.height - 50, "joinLobby")
      .setInteractive()
      .on("pointerdown", () => {
        if (this.lobbyCode.length > 0) {
          this.joinLobby(this.lobbyCode, this.playerName);
        } else {
          alert("Please enter a lobby code");
        }
      });
  }

  joinLobby(lobbyCode, playerName) {
    lobbyCode = lobbyCode.toUpperCase();
    fetch(`http://localhost:5000/lobbies/${lobbyCode}/join`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: playerName,
      }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
      } else {
        this.scene.start('create-lobby-scene', { playerName, lobbyCode, isHost: false });
      }
    });
    }
  }
