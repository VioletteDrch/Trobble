export const server = {
  api: () => {
    return `http://${window?.location.hostname || "localhost"}:4999`;
  },
  websocket: () => {
    return `ws://${window?.location.hostname || "localhost"}:4999/ws`;
  },
};

export function buildBaseWSMessage(playerId, gameId) {
  return {
    player_id: playerId,
    game_id: gameId,
  };
}

export default server;
