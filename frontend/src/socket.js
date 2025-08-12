import { io } from 'socket.io-client';

export const socket = io(`ws://${window.location.hostname}:8000`, {
  path: '/ws/api/get_image'
});