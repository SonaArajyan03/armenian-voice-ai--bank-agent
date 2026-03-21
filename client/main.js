import { Room, RoomEvent } from 'https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.esm.mjs';

const log = document.getElementById('log');
const joinBtn = document.getElementById('join');
const leaveBtn = document.getElementById('leave');
const identityInput = document.getElementById('identity');
let room = null;

function append(message) {
  log.textContent += `\n${message}`;
}

joinBtn.onclick = async () => {
  const identity = identityInput.value || 'demo-user';
  const tokenResp = await fetch('http://localhost:8080/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identity, room: 'bank-support-demo' }),
  });
  const { token } = await tokenResp.json();

  room = new Room();
  room.on(RoomEvent.TrackSubscribed, (track) => {
    if (track.kind === 'audio') {
      const el = track.attach();
      document.body.appendChild(el);
    }
  });
  room.on(RoomEvent.Connected, () => append('Connected. Microphone is live.'));
  room.on(RoomEvent.Disconnected, () => append('Disconnected.'));

  await room.connect('ws://localhost:7880', token);
  await room.localParticipant.setMicrophoneEnabled(true);
  log.textContent = 'Connecting...';
};

leaveBtn.onclick = async () => {
  if (room) {
    await room.disconnect();
    room = null;
  }
  log.textContent = 'Disconnected.';
};
