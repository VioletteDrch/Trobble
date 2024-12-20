import Phaser from "phaser";
import { CardMechanics } from "../public/src/cards/card-mechanics";
import { retrieveSoundEffects } from "../public/src/resources/resource-puller";
import {
  gameRules,
  gameState,
  sizes,
  playerInfo,
  otherPlayers,
} from "../config/gameConfig";
import { server, buildBaseWSMessage } from "../config/serverConfig.js";
import ErrorMessage from "../components/ErrorMessage.js";

export default class GameScene extends Phaser.Scene {
  constructor() {
    super("scene-game");
    this.cardMechanics = new CardMechanics(this);
  }

  preload() {
    retrieveSoundEffects().forEach((sound) => {
      this.load.audio(sound.name, sound.url);
    });
    this.load.image("bg", "/assets/background.jpg");
    this.fetchImages().catch((error) => {
      console.error("Error fetching images:", error);
      this.errorMessage.show(error.message || "Error fetching images");
    });
  }

  init(data) {
    this.ws = data.websocket;
    this.isHost = data.isHost;
    playerInfo.id = data.playerId;
    gameState.gameId = data.gameId;
  }

  create() {
    this.add.image(0, 0, "bg").setOrigin(0, 0).setScale(0.5);
    this.createVictorySign();
    this.errorMessage = new ErrorMessage(
      this,
      this.scale.width / 2,
      40,
      this.scale.width * 0.9
    );
    this.ws.onmessage = (ev) => {
      const message = JSON.parse(ev.data);
      if (message.method === "init") {
        this.initializeGame(message);
      } else if (message.method === "score") {
        this.handleScore(message);
      } else if (message.method === "end") {
        this.gameEnd(message.winner);
      }
    };
    if (this.isHost) {
      this.ws.send(
        JSON.stringify(this.buildInitMessage(playerInfo.id, gameState.gameId))
      );
    }
  }

  initializeGame(initMessage) {
    gameState.middleCard = initMessage.middle_card;
    this.cards = initMessage.cards;
    this.cardMechanics.createCard(
      gameRules.pilePosition.x,
      gameRules.pilePosition.y,
      initMessage.middle_card,
      "pile",
      0x00000,
      () => {}
    );
    this.setPlayersCard(this.cards.pop());
  }

  handleScore(scoreMessage) {
    if (scoreMessage.player_id === playerInfo.id) {
      this.cardMechanics.score(this.currentCard);
      this.setPlayersCard(this.cards.pop());
    } else {
      gameState.blocked = false;
      this.otherPlayerScore(
        scoreMessage.new_middle_card,
        otherPlayers.find((player) => player.id === scoreMessage.player_id)
      );
    }
  }

  setPlayersCard(playersCard) {
    this.currentCard = this.cardMechanics.updatePlayersCard(playersCard);
  }

  otherPlayerScore(newMiddleCard, player) {
    this.cardMechanics.updateMiddleCardWithNewlyCreatedCard(
      newMiddleCard,
      player
    );
  }

  gameEnd(winner) {
    this.time.removeAllEvents();
    if (winner !== gameState.playerName) {
      this.victorySign.text = "YOU LOSE";
      this.victorySign.setFill("#FF0000");
    }
    this.shade.setAlpha(1);
    this.tweens.add({
      targets: this.victorySign,
      scale: { from: 0, to: 1 },
      alpha: { from: 0, to: 1 },
      duration: 1000,
      ease: "Bounce.easeOut",
    });
  }

  createVictorySign() {
    this.shade = this.add.graphics();
    this.shade.fillStyle(0x000000, 0.7);
    this.shade.fillRect(0, 0, sizes.width, sizes.height);
    this.shade.setAlpha(0);
    this.shade.setDepth(60);

    this.victorySign = this.add.text(
      sizes.width / 2,
      sizes.height / 2,
      "YOU WIN!",
      {
        fontSize: "64px",
        fill: "#ff0",
        fontStyle: "bold",
      }
    );
    this.victorySign.setOrigin(0.5);
    this.victorySign.setAlpha(0);
    this.victorySign.setDepth(70);
  }

  isGameActive() {
    return gameState.pileSize <= gameRules.totalAmountOfCards;
  }

  fetchImages() {
    const apiBaseUrl = `${server.api()}/images/`;

    return fetch(`${server.api()}/images`)
      .then((response) => response.json())
      .then((data) => {
        data.forEach((image, index) => {
          const url = `${apiBaseUrl}${image}`;
          const key = `image_${index}`;
          this.load.image(key, url);
        });
      });
  }

  buildInitMessage(playerId, gameId) {
    const initMessage = buildBaseWSMessage(playerId, gameId);
    initMessage.method = "init";
    return initMessage;
  }
}
