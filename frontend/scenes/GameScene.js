import Phaser from "phaser";
import { CardMechanics } from "../public/src/cards/card-mechanics";
import {
  retrieveSoundEffects,
} from "../public/src/resources/resource-puller";
import { gameRules, gameState, sizes } from "../config/gameConfig";
import api from "../config/serverConfig.js";
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
    this.fetchImages()
        .then(() => {
          this.load.start();
        })
        .catch(error => {
      console.error("Error fetching images:", error);
      this.errorMessage.show(error.message || "Error fetching images");
    });
  }

  create() {
    this.load.once("complete", () => {
      this.add.image(0, 0, "bg").setOrigin(0, 0).setScale(0.5);
      this.cardMechanics.createCard( // first middle card
          gameRules.pilePosition.x,
          gameRules.pilePosition.y,
          // imageComb
          [0, 1, 2, 3, 4, 5, 6, 7], // FIXME send from backend instead
          "pile",
          0xfff00,
          () => {}
      );
      this.setPlayersCard();
      this.createVictorySign();
      this.events.on("anotherPlayerScored", this.setMiddleCard, this);
      this.events.on("gameEnd", this.gameEnd, this);
      this.simulateOtherPlayerScoring();
      this.errorMessage = new ErrorMessage(
          this,
          this.scale.width / 2,
          40,
          this.scale.width * 0.9,
      );
    });
  }

  setPlayersCard() {
    // FIXME fetch imageCombination from GameState
    this.cardMechanics.updatePlayersCard([0, 1, 2, 3, 4, 5, 6, 7], () => {
      this.setPlayersCard();
    });
  }

  setMiddleCard() {
    // FIXME fetch imageCombination from GameState
    const otherPlayersCard = this.cardMechanics.updateMiddleCard(
            [0, 1, 2, 3, 4, 5, 6, 7], "violette", 0x7f00ff, () => {}
        );
  }

  simulateOtherPlayerScoring() {
    this.time.addEvent({
      delay: 2000,
      callback: () => {
        this.events.emit("anotherPlayerScored");
      },
      loop: this.isGameActive(),
    });
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

  fetchImages(){
    const apiBaseUrl = `${api.host()}/images/`;

    return fetch(`${api.host()}/images`)
        .then(response => response.json())
        .then(data => {
          data.forEach((image, index) => {
            const url = `${apiBaseUrl}${image}`;
            const key = `image_${index}`;
            console.log(key)
            this.load.image(key, url);
          });
        })
  }
}