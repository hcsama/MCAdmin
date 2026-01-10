<script lang="ts">
    import { Plane, Send, CheckCircle2 } from 'lucide-svelte';
    import { fade, fly } from 'svelte/transition';

    let { serverOnline = true } = $props();
    
    let message = $state('');
    let sending = $state(false);
    let showSuccess = $state(false);
    let successTimeout: ReturnType<typeof setTimeout>;

    async function handleSend() {
        if (!message.trim() || sending || !serverOnline) return;

        sending = true;
        try {
            const response = await fetch('/api/server/broadcast', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message.trim() })
            });

            if (response.ok) {
                message = '';
                showSuccess = true;
                if (successTimeout) clearTimeout(successTimeout);
                successTimeout = setTimeout(() => {
                    showSuccess = false;
                }, 3000);
            }
        } catch (error) {
            console.error('Failed to send broadcast:', error);
        } finally {
            sending = false;
        }
    }

    function handleKeyDown(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            handleSend();
        }
    }
</script>

<div class="col-span-full bg-white dark:bg-slate-900 rounded-3xl p-4 shadow-sm border border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row items-center gap-4 transition-all hover:shadow-md relative overflow-hidden group">
    <!-- Visual Accent -->
    <div class="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-amber-400 to-orange-500 opacity-20"></div>
    
    <div class="flex items-center gap-3 shrink-0">
        <div class="w-10 h-10 rounded-2xl bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center text-amber-600 dark:text-amber-400 group-hover:scale-110 transition-transform">
            <Plane size={20} />
        </div>
        <div class="flex flex-col">
            <h2 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Broadcast</h2>
            <p class="text-sm font-semibold text-slate-700 dark:text-slate-300">Message to All</p>
        </div>
    </div>

    <div class="flex-1 w-full flex flex-col gap-1.5 min-h-[44px] justify-center">
        <div class="flex items-center gap-2">
            <input
                type="text"
                bind:value={message}
                onkeydown={handleKeyDown}
                placeholder={serverOnline ? "Type a message to all players..." : "Server offline"}
                disabled={!serverOnline || sending}
                class="flex-1 bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-700 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/50 transition-all disabled:opacity-50"
            />
            
            <button
                onclick={handleSend}
                disabled={!message.trim() || sending || !serverOnline}
                class="shrink-0 h-9 px-4 bg-amber-600 hover:bg-amber-700 disabled:bg-slate-200 dark:disabled:bg-slate-800 text-white rounded-xl font-bold text-sm flex items-center gap-2 transition-all active:scale-95 disabled:scale-100 disabled:opacity-50"
            >
                {#if sending}
                    <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                {:else}
                    <Send size={16} />
                {/if}
                <span class="hidden sm:inline">Send</span>
            </button>
        </div>

        {#if showSuccess}
            <div 
                transition:fly={{ y: -5, duration: 300 }}
                class="flex items-center gap-1.5 text-green-600 dark:text-green-400 text-[11px] font-bold px-1"
            >
                <CheckCircle2 size={12} />
                Message sent successfully to all players
            </div>
        {/if}
    </div>
</div>
