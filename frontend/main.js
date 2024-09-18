import "./style.css";
import Phaser from "phaser";
import { sizes } from "./config/gameConfig";
import StartScene from "./scenes/StartScene";
import LobbyScene from "./scenes/LobbyScene";
import JoinLobbyScene from "./scenes/JoinLobbyScene";
import GameScene from "./scenes/GameScene";

const config = {
  type: Phaser.WEBGL,
  width: sizes.width,
  height: sizes.height,
  backgroundColor: "#FFFFC0",
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH
  },
  canvas: gameCanvas,
  physics: {
    default: "arcade",
    arcade: {
      gravity: { y: 0 },
      debug: false,
    },
  },
  scene: [StartScene, LobbyScene, JoinLobbyScene, GameScene],
  // scene: [GameScene],
};

const game = new Phaser.Game(config);
