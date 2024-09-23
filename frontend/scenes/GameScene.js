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
    this.fetchImages();
    retrieveSoundEffects().forEach((sound) => {
      this.load.audio(sound.name, sound.url);
    });
    this.load.image("bg", "/assets/background.jpg");
  }

  create() {
    this.add.image(0, 0, "bg").setOrigin(0, 0).setScale(0.5);
    const pile = this.cardMechanics.createCard(
      gameRules.pilePosition.x,
      gameRules.pilePosition.y,
      // imageComb
        [0, 1, 2, 3, 4, 5, 6, 7], // FIXME send from backend instead
      "pile",
      0xfff00,
      () => {}
    );
    this.createPlayerCard();
    this.createVictorySign();
    this.events.on("anotherPlayerScored", this.putOtherPlayersCardOnPile, this);
    this.events.on("gameEnd", this.gameEnd, this);
    this.simulateOtherPlayerScoring();
    this.errorMessage = new ErrorMessage(
        this,
        this.scale.width / 2,
        40,
        this.scale.width * 0.9,
    );
  }

  updateMiddleCard() {

  }

  updatePlayersCard() {

  }

  createPlayerCard() {
    this.cardMechanics.createCard(
      150,
      370,
        [0, 1, 2, 3, 4, 5, 6, 7], // FIXME send from backend instead
      gameState.playerName,
      0x0000ff,
      () => {
        this.createPlayerCard();
      }
    );
  }

  putOtherPlayersCardOnPile() {
    const otherPlayersCard = this.cardMechanics.createCard(
      300,
      300,
        [0, 1, 2, 3, 4, 5, 6, 7], // FIXME send from backend instead
      "violette",
      0x7f00ff,
      () => {}
    );
    this.cardMechanics.score(otherPlayersCard);
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
    fetch(`${api.host()}/images`)
        .then(response => response.json())
        .then(data => {
          data.forEach((image, index) => {
            const url = `${apiBaseUrl}${image}`;
            const key = `image_${index}`;
            console.log(key)
            this.load.image(key, url);
          });
        })
        .catch(error => {
          console.error("Error fetching images:", error);
          this.errorMessage.show(error.message || "Error fetching images");
        });
  }
}