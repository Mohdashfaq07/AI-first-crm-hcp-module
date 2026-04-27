import { configureStore, createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import axios from 'axios';
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const fetchInteractions = createAsyncThunk('crm/fetch', async()=> (await axios.get(`${API}/interactions`)).data);
export const createInteraction = createAsyncThunk('crm/create', async(data)=> (await axios.post(`${API}/interactions`, data)).data);
export const updateInteraction = createAsyncThunk('crm/update', async({id,data})=> (await axios.put(`${API}/interactions/${id}`, data)).data);
export const sendChat = createAsyncThunk('crm/chat', async(message)=> (await axios.post(`${API}/agent/chat`, {message})).data);
const crmSlice = createSlice({name:'crm', initialState:{items:[], chat:[], loading:false}, reducers:{}, extraReducers:(b)=>{
 b.addCase(fetchInteractions.fulfilled,(s,a)=>{s.items=a.payload});
 b.addCase(createInteraction.fulfilled,(s,a)=>{s.items.unshift(a.payload)});
 b.addCase(updateInteraction.fulfilled,(s,a)=>{s.items=s.items.map(x=>x.id===a.payload.id?a.payload:x)});
 b.addCase(sendChat.pending,(s)=>{s.loading=true});
 b.addCase(sendChat.fulfilled,(s,a)=>{s.loading=false; s.chat.push(a.payload); if(a.payload.interactions?.length) s.items=[...a.payload.interactions,...s.items]});
}});
export const store = configureStore({reducer:{crm:crmSlice.reducer}});
