import Phaser from "phaser";

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
      "Klovn"
    ];

    const titles = [
      "Konge",
      "Dronning",
      "Entusiast",
      "Mester",
      "Lord",
      "Ekspert"
    ]

    const word1 = objects[Math.floor(Math.random() * objects.length)];
    const word2 = titles[Math.floor(Math.random() * titles.length)];
    const number = Math.floor(Math.random() * 99) + 1;

    return `${word1}${word2}${number}`;
  }

  create() {
    this.cameras.main.setBackgroundColor("#FFFFC0");
    this.logo = this.add
      .image(
        160,
        160,
        "logo"
      ).setScale(0.6);

    this.enteredName = this.generateRandomName();

    this.add
      .image(
        this.scale.width / 2,
        this.scale.height / 2 + 115,
        "createLobby"
      )
      .setInteractive()
      .on("pointerdown", () => {
        if (this.enteredName.length > 0) {
          this.createLobby(this.enteredName);
        } else {
          alert("Please enter a name");
        }
      });

    this.add
      .image(
        this.scale.width / 2,
        this.scale.height - 50,
        "joinLobby"
      )
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
    fetch("http://localhost:5000/lobbies", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        host_name: playerName,
        private: false,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        const lobbyCode = data.lobby_code;
        this.scene.start("create-lobby-scene", {
          playerName,
          lobbyCode,
          isHost: true,
        });
      });
  }

  joinLobby(playerName) {
    this.scene.start("join-lobby-scene", { playerName });
  }
}
