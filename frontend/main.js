import "./style.css";
import Phaser from "phaser";
import { sizes } from "./config/gameConfig";
import StartScene from "./scenes/StartScene";
import CreateLobbyScene from "./scenes/CreateLobbyScene";
import JoinLobbyScene from "./scenes/JoinLobbyScene";
import GameScene from "./scenes/GameScene";

const config = {
  type: Phaser.WEBGL,
  width: sizes.width,
  height: sizes.height,
  canvas: gameCanvas,
  physics: {
    default: "arcade",
    arcade: {
      gravity: { y: 0 },
      debug: false,
    },
  },
  scene: [StartScene, CreateLobbyScene, JoinLobbyScene, GameScene],
};

const game = new Phaser.Game(config);
