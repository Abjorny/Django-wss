import { io } from 'socket.io-client';

export const socket = io("ws://${window.location.hostname}:8000/ws/api/get_image");