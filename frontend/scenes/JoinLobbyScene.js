import Phaser from "phaser";

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
  }

  create() {
    this.cameras.main.setBackgroundColor("#FFFFC0");

    this.titleText = this.add.text(this.scale.width / 2, 50, "Select a lobby:", {
      fontSize: '28px',
      fill: '#c671ff',
      fontStyle: 'bold',
      align: 'center'
    }).setOrigin(0.5);

    this.lobbiesContainer = this.add.container(this.scale.width / 2, 100);

    this.lobbiesList = this.add.text(0, 0, "Loading lobbies...", {
      fontSize: '24px',
      fill: '#c671ff',
      align: 'center'
    });

    this.lobbiesContainer.add(this.lobbiesList);

    this.refreshButton = this.add.image(this.scale.width / 2, this.scale.height - 50, "refresh")
      .setInteractive()
      .on("pointerdown", this.fetchLobbies.bind(this))
      .setOrigin(0.5);

    this.fetchLobbies();
  }

  fetchLobbies() {
    fetch('http://localhost:5000/lobbies')
      .then(response => response.json())
      .then(lobbies => {
        this.updateLobbiesList(lobbies);
      })
      .catch(error => {
        console.error("Error fetching lobbies:", error);
      });
  }

  updateLobbiesList(lobbies) {
    this.lobbiesContainer.removeAll(true);

    if (lobbies.length === 0) {
      this.lobbiesList.setText("No lobbies available");
      return;
    }

    lobbies.forEach((lobby, index) => {
      if (index >= 5) {
        return;
      }
      const lobbyCode = lobby['lobby_code'];
      const button = this.add.text(0, index * 60, lobbyCode, {
        fontSize: '30px',
        fill: '#fff',
        backgroundColor: '#c671ff',
        padding: { x: 10, y: 5 }
      }).setInteractive()
        .on('pointerdown', () => {
          this.joinLobby(lobbyCode, this.playerName);
        }).setOrigin(0.5);

      this.lobbiesContainer.add(button);
    });

    this.lobbiesContainer.setPosition(this.scale.width / 2, 100);
  }

  joinLobby(lobbyCode, playerName) {
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
    })
    .catch(error => {
      console.error("Error joining lobby:", error);
    });
  }
}

