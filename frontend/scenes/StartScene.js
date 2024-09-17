import Phaser from "phaser";

export default class StartScene extends Phaser.Scene {
  constructor() {
    super("scene-start");
  }

  preload() {
    this.load.image("createLobby", "/assets/create-lobby.png");
    this.load.image("joinLobby", "/assets/join-lobby.png");
  }

  create() {
    this.cameras.main.setBackgroundColor("#FFFFC0");
    this.nameText = this.add.text(this.scale.width / 2, this.scale.height / 2 - 50, "Enter your name:", {
      fontSize: '32px',
      fill: '#c671ff',
    }).setOrigin(0.5);

    this.enteredName = "";

    this.input.keyboard.on('keydown', (event) => {
      if (event.keyCode === 8 && this.enteredName.length > 0) {
        this.enteredName = this.enteredName.slice(0, -1);
      } else if (event.key.length === 1 && this.enteredName.length < 15) {
        this.enteredName += event.key;
      }
      this.nameText.setText(`Enter your name: ${this.enteredName}`);
    });

    this.add.image(this.scale.width / 2 - 150, this.scale.height / 2 + 50, "createLobby")
      .setInteractive()
      .on("pointerdown", () => {
        if (this.enteredName.length > 0) {
          this.createLobby(this.enteredName);
        } else {
          alert("Please enter a name");
        }
      });

    this.add.image(this.scale.width / 2 + 150, this.scale.height / 2 + 50, "joinLobby")
      .setInteractive()
      .on("pointerdown", () => {
        if (this.enteredName.length > 0) {
          this.joinLobby(this.enteredName);
        } else {
          alert("Please enter a name");
        }
      });
  }

  createLobby(playerName) {
    fetch('http://localhost:5000/lobbies', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        host_name: playerName,
        private: true,
      }),
    })
    .then(response => response.json())
    .then(data => {
      const lobbyCode = data.lobby_code;
      this.scene.start('create-lobby-scene', { playerName, lobbyCode, isHost: true });
    })
    .catch(alert("Something went wrong"));
  }

  joinLobby(playerName) {
    this.scene.start('join-lobby-scene', { playerName });
  }
}

