<script lang="ts">
	import { onMount, onDestroy, untrack } from 'svelte';
	import StatusBar from '$lib/components/StatusBar.svelte';
	import PlayerList from '$lib/components/PlayerList.svelte';
	import WhitelistCard from '$lib/components/WhitelistCard.svelte';
	import WeatherCard from '$lib/components/WeatherCard.svelte';
	import GamerulesCard from '$lib/components/GamerulesCard.svelte';
	import BroadcastTile from '$lib/components/BroadcastTile.svelte';
	let { data } = $props();
	
	// Use untrack to prevent Svelte 5 warning about capturing initial value
	// Initial state structure matching the new decomposed API models
	let liveStates = $state(untrack(() => data.status));
	let eventSource: EventSource | null = null;

	onMount(() => {
		eventSource = new EventSource('/api/status-stream');
		
		eventSource.onmessage = (event) => {
			try {
				const { domain, data } = JSON.parse(event.data);
				if (domain === 'all') {
					liveStates = data;
				} else if (liveStates[domain]) {
					liveStates[domain] = data;
				}
			} catch (error) {
				console.error('Failed to parse SSE data:', error);
			}
		};

		eventSource.onerror = (error) => {
			console.error('SSE connection failed:', error);
			liveStates.server = { ...liveStates.server, online: false, error: 'Live updates disconnected' };
		};
	});

	onDestroy(() => {
		if (eventSource) {
			eventSource.close();
		}
	});

	let server = $derived(liveStates.server);
	let world = $derived(liveStates.world);
	let players = $derived(liveStates.players);
	let whitelist = $derived(liveStates.whitelist);
	let gamerules = $derived(liveStates.gamerules);
</script>

<StatusBar {server} {world} />
{#if server.online}
	<div class="mb-6 flex flex-col gap-6">
		<BroadcastTile serverOnline={server.online} />

		<div class="grid gap-6 lg:grid-cols-3">
		<!-- Players Card -->
		<div class="rounded-2xl border border-slate-200 bg-emerald-50/40 p-6 shadow-sm backdrop-blur-sm transition-all dark:border-slate-800 dark:bg-emerald-900/10 group/tile">
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-lg font-semibold text-slate-900 dark:text-white">Players</h2>
				<div class="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 dark:bg-slate-800">
					<span class="text-xs font-bold text-slate-600 dark:text-slate-400">
						{players.online} / {players.max}
					</span>
				</div>
			</div>
			
			<div class="h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800">
				<div 
					class="h-2 rounded-full bg-green-500 transition-all duration-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]" 
					style="width: {players.max > 0 ? (players.online / players.max) * 100 : 0}%"
				></div>
			</div>

			<PlayerList players={players.list} />
		</div>

		<!-- Whitelist Card -->
		{#if whitelist}
			<WhitelistCard {whitelist} serverOnline={server.online} onlinePlayers={players.list} />
		{/if}

		{#if world}
			<WeatherCard {world} serverOnline={server.online} />
		{/if}

		<!-- Gamerules Card -->
		{#if gamerules}
			<GamerulesCard {gamerules} serverOnline={server.online} />
		{/if}
		</div>
	</div>
{/if}
