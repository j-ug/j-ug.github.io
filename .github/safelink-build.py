"""Assemble the SafeLink Pages build from the existing standalone atlas."""

from html import escape
from pathlib import Path

VOICE_ENDPOINT = 'https://safelink-voice.jeswinsamuel-la.workers.dev/token'

STYLE = r"""
.safelink-dock { display: none; }
.safelink-connectivity { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem .9rem; margin: .1rem auto .9rem; font-size: .78rem; font-weight: 850; color: #3d4936; }
.safelink-connectivity span { display: inline-flex; align-items: center; gap: .4rem; }
.safelink-connectivity [hidden] { display: none; }
.safelink-connectivity span::before { content: ""; display: block; width: .48rem; height: .48rem; border-radius: 50%; background: #507741; }
#safelink-network[data-online="false"]::before { background: #98622c; }
#safelink-cache { color: #59634d; }
.safelink-has-dock #workspace, .safelink-has-dock #journey { scroll-margin-top: 4.5rem; }

.ride-settings { padding: clamp(18px, 4vw, 26px); }
.ride-head h2 { font-size: 1.55rem; }
.ride-settings .ride-icon, .ride-settings input, .ride-settings select, .ride-settings .ride-primary { min-height: 44px; }
.ride-settings .ride-icon { width: 44px; }
.ride-settings .ride-audio input { min-height: 0; }
.ride-settings .call-options { margin-top: .85rem; }
.call-cloud { margin-top: .8rem; padding: .7rem .85rem; border: 1px solid #c7ceba; border-radius: 10px; background: #edf0e3; }
.call-cloud label { display: grid; gap: .3rem; font-size: .83rem; font-weight: 850; }
.call-cloud input { width: 100%; padding: 6px 9px; color: #263020; background: #fffdf5; border-radius: 7px; border: 1px solid #a8b29e; font: inherit; }
.call-cloud p { margin: .55rem 0 0; font-size: .76rem; }
#call-setup-note:empty { display: none; }
.ride-screen .ride-display { padding-top: clamp(42px, 11svh, 110px); padding-bottom: max(26px, env(safe-area-inset-bottom)); }
.ride-screen .ride-avatar { width: 86px; height: 86px; border: 1px solid #657468; box-shadow: 0 0 0 10px #2c3831; }
.ride-screen[data-live="true"] .ride-avatar { border-color: #91deb2; }
.ride-screen #ride-pickup { font-size: .87rem; font-weight: 850; color: #d2e5d9; padding: .5rem .85rem; background: #29382f; border-radius: 22px; max-width: 340px; }
.call-voice-tools { width: min(100%, 360px); margin-top: 1.1rem; }
.call-replies { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
.call-replies[hidden] { display: none; }
.call-replies button, .call-mute { font: inherit; font-size: .83rem; font-weight: 850; min-height: 44px; padding: .45rem .82rem; color: #f1f6ef; border: 1px solid #66776b; background: #202e26; border-radius: 24px; }
.call-replies button:hover, .call-mute:hover { background: #33473b; }
.call-mute[aria-pressed="true"] { border-color: #fed395; color: #fed395; }
.call-caption { min-height: 1.6em; margin: .65rem 0 0; color: #d6e0d5; }
.call-caption:empty { display:none; }
.ride-screen .ride-controls { padding-top: 3rem; padding-bottom: .7rem; }
.ride-screen .ride-controls button { min-width: 111px; min-height: 52px; }

@media (max-width: 740px) {
  .safelink-has-dock { padding-bottom: calc(65px + env(safe-area-inset-bottom)); }
  .safelink-dock { position: fixed; z-index: 29; bottom: 0; left: 0; right: 0; display: grid; grid-template-columns: repeat(4,minmax(0,1fr)); padding: 5px max(7px, env(safe-area-inset-right)) calc(5px + env(safe-area-inset-bottom)) max(7px, env(safe-area-inset-left)); gap: 3px; border-top: 1px solid #cdd2bd; background: #f8f6eb; box-shadow: 0 -5px 22px #303b2823; }
  .safelink-dock button { display: grid; min-height: 48px; place-content: center; justify-items: center; gap: 1px; border: 0; border-radius: 7px; background: transparent; color: #293824; font: inherit; font-size: .74rem; font-weight: 900; }
  .safelink-dock button span { font-size: 1.12rem; line-height: 1.05; }
  .safelink-dock button:last-child { background: #f0e2dc; color: #742a27; }
  .safelink-dock button:focus-visible { outline: 2px solid #385d36; outline-offset: -2px; }
  .safelink-upgrade #ride-open, .safelink-upgrade #top-sos { display: none; }
  .ride-timer { bottom: calc(66px + env(safe-area-inset-bottom)); }
}

.call-cloud .call-preview { display: flex; }
.call-cloud .call-preview input { width: 17px; min-height: 17px; }
"""

CLIPS = r"""
/* English fallback clips generated with the Flite SLT voice. */
window.safeLinkRideClips = {
  "hello": "data:audio/mpeg;base64,SUQzBAAAAAAAIlRTU0UAAAAOAAADTGF2ZjYxLjcuMTAzAAAAAAAAAAAAAAD/8yjEAAtINjQAMkwgTc4ACyQYYTCCZxBTogAZAPtGn6wf//pEBPie/0/36z/LlyBPkMo45l///hjJqgGkBsLj7YfEx1HaAQv/8yjEDQtwMmQUSkwEbCMX0Xf//ShnTnFh/kL9s4sogmQDChQSJU56/rRmf/+2whgPj+ACBUBZoYzrUx///9vpUz8ip9zfvPT/8yjEGg0IMlgCQxAAbLBQVIhxaEEjwZBoJwyBpk081ah3tdaiNqTVAAvVneN9LbeJRLija+pSe3fput3/jvZUuz/9G3XZ22b/8yjEIAo4HoJ+CIIArHW8W/v91QweBFzAGFtUCaDJKLCCweWCyRVRahm+odZ3afXX16l9H62rtr3heVffkmMFE31Ob2vp/rf/8yjEMgy4JlTsY9IA1zERUOPcQQBxOeQZvN80ifL//1+P/73/tEb2iI8OQzH17MhyZNMmTPTMvsQiH0wnrlBB5wAVz1oA6Zn/8yjEOhfTEmwKQA0IjXqDkydtDRHbGiNMQfYggqM78zPGtGf/778EIz//+Hu/3uzCBBV70BBw4oOZt0W9/8/5G////96ulyH/8yjEFRG58pgAEIy8EJ2F7/5vP2DMa6oLiHB0pKjQcLOdAfZS1JOitgkFiTkpXCFIPjgy4MQK+j+qLrfCKyYP3kP99BOAHDb/8yjECQ55RrTKQEacLoqTYMsF+BftP/9eUXzN03KHEr1BbBcLE4qoaBZQOizgdUoY9lX23oFSFLH///W+L5r//3PQAL/cbVj/8yjECg846s5Y1lZMTTMU4Pc+XYICigGo0JhoggHlXfZ3Zi7DTPDLycqRCY0ENe/Zki2+aPA4QqkJqNUbdfWsMackYSgAfar/8yjECA5RCtJYDk4cR9xTA4j4hKJFI8HwBSNFuYuaiQYi92MxN09Mvyj/X5R/gQbeo4T9UJ00Qn///0anZCoIBcdSPwAgPUX/8yjECQ8JBt5ci9pQkN0CNm3vPViF+hzjJ+/LU6miAuGQzFf8Y/1jqe6kBof0B2H01ay4QqBTp//+jU7Z/rv01QQDDtcgCmf/8yjEBw4RBuY8glSKzEjgfPOvGfEyJ8RfAPRJpXcBJBR6KHjZswTfjAKEkfoNprajIvq///7dbv+zv///+tUAMWW3ABDwsMr/8yjECQ7Iysm6Dl4gx9+3tt1oaIzl+DFr0ScBk0i20wCVifebogRl/DeQoRdhb2bOseEjn4a0/////yH/2sQqCAEEbUtAhxb/8yjECA24/uZaC9Y6iwiv5ddJwFmrR8QEAnXcV+5C6TXx8YoLsm25WCdH7DQBhZ/6DJj9B+f1f///n9UgEWnID0JmMUU2ryL/8yjEDAypAumYasZ+trJdefIVz4mwUMr/TIb/pAhH+x+GY+s3MBLEFW8fF0PrP5T///C6DEOBET2A6lj8CODKW5iqAx0Z0HD/8yjEFAtxEupYacx8CranCQAa3iKuqsTbyo2O7CInKgAJbDRCOAISYBgpR6h9hXzLakjmXnVp8Tj7dW9bn4SYVfUPGfsBhbr/8yjEIQzAwtWSk8pQEFtRLAuzId32bMu7O3CH/9gUXShy3QLxDYSn626RVWd/tmbZY229/qMLWnkygZ9RwlzBoSxDg5lHUt//8yjEKQxotsyqDg4Y/8cBloPf/19l7rurYyGBZGIR2zpEAFdPNLECXnEzYxOwAxkd/VsYZsXUARXkDaaCIrgq6V//////2cP/8yjEMgzAyrgA08pwr0DH/xHgBEeF9BCCmtkfeC4YZ1Ft+6gI7cxuhnzcugEKbLf9XXbd/t2k0V/+dtDZkeNSLkHhSD0wocD/8yjEOgy4rsR+DgQMZUD4vnxVd8SnTv//56gOmUIROs21GqtTwqdArkj3eW3D2w6riUAztbv9OSJVDAWYHGToDBsdFKyIGpL/8yjEQgzYNog0MwAkT////6lLTPDNIdXWJU2wmIhUktB1oiYRHrctskgFUNVduoX9pJBEIwGgDgAJQ6DyrgAcaZ////9KZi7/8yjESQz4LlwKSxIA2ZGlCVMUSdjnpLNpYLkKAFHjtbVUWrFC/Z3ITi8rRipBSHg1wHnls+r///+29Bc2y27VpVohstRWHnL/8yjEUAwAKlAAYlgAhzFoDFqViiWKF27ovZNMlEES/TKlRlWMtQx+kVF8D8v3ufnw+88r3vl/0s/+ZFC/5sR5/P+I6NdirBf/8yjEWwwAJlQBTwAAJmzZ6vFlBqS/QXTnYRH5km6+6kOFMT+rzoRjJCJXYp1sgHIbb5v+LEN01SYbT2FnUxUAIAaiigiSggD/8yjEZhcaekwBmBgB/0ig///HTXf5bjB7FS/wmIdiFTkWqiL+Z2HwBFMCiMD5eZf/+1yzt/1w36VV/udliKIBYeXGjuNyfRP/8yjERBfiar2VgkAAf+f1EIsQAmEsCV43j7qWG4C/lGyqBAee1PMhRUd0iPLY3Ii3xv9KjRic81Q8+GqMMXV1l72hsbaEq1v/8yjEHxH48t7/yTAAY792oz/d6UY/ckTaCp8e68ueuWi/Ow6tTxQ1lgz/uQWxQ02mr//9LTJSXbOIkfQTAEgCVo2MSNJMG4//8yjEEhCRNtpIm8o8u8fjDPGTc0Mb7TmHMMBNQmGDOi1uTXuExfxNPb2K/ij3w+dkw++T2dlxyfz+//166kaM8gS9KkEYAmD/8yjECg8pCt5Ak8pwSI4rDXErCh22MhTxrT7EcgZ9movU38RDG6jn6l9DehvQWdBR0W1YriOoG3wk9Yz//Tx1hZbkltZSMB7/8yjECA6g3v5ca9SO2KgUqC8rGR+hREIzfUgfxbZ62yX0pP8Vg0fj4T/QmbmkTq9evLaXbt+fwssqz/+TatiFhCIe2gIIB+P/8yjECA0Iytm8C84MIUI+1QxwZ2E+qegRAVak4Cx7VUF+x0E1WZFvyvD2ZrJ7dmz6NF6K//163QCqqllZWePqBffiIJ2vTPT/8yjEDgvQ3x54WlaSDH/MuGdxOYjCHk7RsRfZYoJJ7TZEzNj3qf8rWCawLbNK6kKpPv/9rdqBgViKbPaVyLfZkqE45cjLoHT/8yjEGQy4xwpYUwQ+fV0djpOJLn1odO22qMvhRNRColgrs+37pN2B6yvUjjAArO3qoWxgwHx4EpqCFacREzN+JvUPmGAhVHb/8yjEIQ0YYowA5oxIuiz/////eYOiBposJQh///2UMWqf1VZUCCcw6jO+0aHnkqgoXOCS9khd05n////+U9qpNys4QEBJZ8v/8yjEJwz4SqQA3hAkkBp/Lp24oNQOE5B8CT6lmBPgZAKAyLFKFYvsPge0NZg3v60P/+v1c+dGpQot5LFIrscK4u8iZbv+vVL/8yjELgwh1rQAoAUMQv6VSDdttAjJcB8rcdQTf0wP7lfqigeoWblAZkC269eHKQZP5d//9fTmHf1cxWL6P/1O1EQRff/wCDD/8yjEOAw4aupcC/ASHqqI0CQepOi0Xeso3DwVgHBdTpMA3V8a/qL5TVqd/9evaH9tTdP/+eDeClUSwT//ED1jUEnQ2NhajrP/8yjEQgyInuJchgpoOXCLtfwqAcndukHT+cBxbyL538gc9TvxAOBlQYfB09u3fWpIJRO2xkjP1L+PLfxmGU1vCSOyCNNbXN//8yjESgxZGuW4awpwEueNKKJTiLPd7q4IhrcoQAYCUva7bv7RggRxvYKIcnRABgLmY/487CLqQVpouNKOslYSgbzS8gjpX+b/8yjEUxDhKvJYC9IeZYRwDOti3HwPG9Q4XzpwVRgWeg6dzQDkPZIk/I6zstiE9Tz38IHoJbf/8BHQ5//cBFlDSyRcUkKBVBP/8yjEShGw2vZee06qjKdEgFC1MAMAZUyu9p78sGE0MhvM/mM2hwreb5pjP736GcMXMGNzJZ6F8c0rvp//nlCQ8L//o+T11RD/8yjEPg8JOtW+CwQOXb+4BQqmAIKkl////54CgWAnnisOmCQNG0YUI4pI7oo6dPBIsoKjCz/6GXWegS9QND2GT5GhhMQgYZb/8yjEPAywKpi+AMwAhR1NrkaZuV////9OsxSnYrRoAH5ixbtgoQuVEUeoCG26dqqVKjRRJliyBygI51HGbxXAWcW1SK5W5Fb/8yjERAtILlABTxAAdf7f/b3T/TUhk9dj2u2CGE0NGKbvoQ4g7Gcowt2cz0VeTU7qBmd+TUpAwc5nVnz1VJzuQ7vumVAYmJX/8yjEURZ7EmABjxABMZFf3o5lUbnVnv14znvm4/r0+fajn/0/9F////+fmZcoe6oqGnFSjeY2LGJiwgUFg4agPxCNRQNy4nD/8yjEMhcrIrABiTgAmzM/8wOOIDh6HmEEOHwdFkNPNMH0LL/n/tMOMQojHjdnMozMdQ9zx1h4qrd72mHXZtYBa/O7TkhI9R7/8yjEEBDglwp92sACHiTgyxuqGKFfPtadtMPufs8KhEcMEwhucU9RUBXkVfLUrshFgny+I8hkP8QHJK5v0XJ+ikQjWnbaiGD/8yjEBw5g3vJcW87mL/gKAjHL0Rz5PNAxBr45Bna8ljk23iPtMkOxbcQiQ/KkNpQg8gI8Ru8TZHXq+nVp0/6qBplthQg4OWz/8yjECA3wrtEaDhIEhAUonarkgMA1e+IDg1BHsAdEv3Hh4Go/4VNf3zrOSyGR9rcNLPLOxNr2+p5EWEpGABz+/42l9SRo3Xv/8yjECwvwwvZYA9AaYO4wDjSvyiiRKA6mVXGt/m6KOX3Bq34qEX+Rf2/+t38+QKGfrgAIJHIASL/3Yww8xW0Dzj0/B0qKlbf/8yjEFgyQprpS1hQwUdvjwDwXPm6bMYgn6fbyMTs1////dGH6////5OodR70WNKwa2kM9Gch1CTZ848SRYKPbB9v3////21H/8yjEHgxQYrwAHkoQxCjgsUBAoLEoWzWf0UHGCp+Ce+qsAwwB9ZwCPh3ppuahg8YD5wPwGTUypY+h//39G9K7oy9X7lfKy6n/8yjEJwwKJsxUmAUMSk/PZSFHgEMUVUCIVLbLCjAe1QEIO511hpBYj4XkomYpNx3t4pvC/C/X7fb0Kp5FNC9adlAWenTo////8yjEMQ0BTuZcaIbyooRoAcKspQBA4LrVDHAbI/UaiuMHMnnKf4iraGxLWV+Qvq1f/9VP+i9syQaUw9//////7ywHLddmkTD/8yjEOAxAesGuDhQQH1F8bwKi+cEvTOtDJKenwwG6GwVDStoX6oLPRfHT/p9Yti2qwHfjtH//9SpkPe7/8AKQAPSooCXldyb/8yjEQgyI3t5cg85qzuRXL3OQ3dGQDXe//hYGHe4RJMw3kNmR///+p275//dsYwlVQCMbkkZJQ9qg8yfvOXaqkd8n4i4QGw3/8yjESgyIgwJePhJOD7kKEAdbyBAU9H9BTL6dev5d8bFRpxk/n9Gj/6tSIrLkkhA7sQgzPQWZB7NqkjIKkbaJmEzKTG8zEbb/8yjEUg0osuZaVgoy6x2egIb1H+NPeSz2yzQeA0kl+hWJMrrqPh+WQKiCOlp2hnePLOKYLoIDnyXRZcsdjx7Hz703/wSDX+T/8yjEWA0RKvG4aJcm3PfvJZN5pMdY+VR1oqAlOmqDiWfh7eCa3uDSX5aW2pRoGhwAP8MboT0XMNqHoCae71cvxPlcp2Q8ONb/8yjEXg/xQswok9ZTTEUj4DXbQZ8qZ8bfb5vqb838u1ymjb//9Wn66gTHJHGlHoLUAtgbarYJ4RNkYayM3BLyU8vjspNX2fH/8yjEWQ5RZum+C84WIDPxgGJUYgt4i2WRXZ4iySoShM7nau6rtpqe7QSlKYxOgO4J24xAyiZV5W/OxnUQRuVdzHqQwYrfvlH/8yjEWg4g8tG4m8o2++rVqoWHoqH5cPh8gDgYK7ayGGKwxW+s/n5R0pVglzTbACa4AP4lBp4qBabhPEUPXWI/qHPjvkQ39Pn/8yjEXA9YZqgA3lIwCftLPuoNCtYPBLGQ9LmCsCAYzKVahkz5nVDE5hK5pIcaLHUiOcasgLrroDWA9sdwar4jhKFtWNoWNBP/8yjEWRE6awJeUBVLjR2UN/29YwX3/9PnbOgFbQGet3+5igoaW6PqQC93xAd1jlZEIyLtD2tKUk2O5c7gLNw6/ALltIfL0J//8yjETwuRyum0aAVKoRhZb///+hs/EoOjHhn//qFg1KUhCr//iABkPUTKk6Xrwz+MtDhV0/izA9GSLwuKlbFRvlDvFJH/////8yjEWwzorsmkwxSE9UgBVyypH/9IwSxZQI8v/CoAFUVuJHSRMd3Z6rBiZzLpmPWcfm/iFC5weffX////63WKC6VhA9W7/1P/8yjEYgywrspGDk4MjBI5TUkhmMDAOgARi9jAC0nQ+7/og4w2vpyX8Hf////+SVBUaRCphRu8HqP9QaLGziGAoSUYAQGTgEj/8yjEag0AYr5GHhIM2EYIlgJrhYstk/9oJJO///6x6VucRLFrAoB3BI0nPAH9XUaQWyJb//xw5WcaNJha8WCMZmBGEv7JRT7/8yjEcQvgTrZGDgwE5//6px90VFSynjxvrda4BCrjFej4sHTKxwlQxn//zaBGAgAu02wGJgoqe/lSS2//70lqCgVIuXJUpa7/8yjEfAwgNp0OCxAEQj9R60GjV+qw8hNU9BYCnXO//YKAVA6BCJZGGgTACIFQAMA6I4iRKFp3Zf+id9030X/+j/b9Omu2zoH/8yjEhgw4MoQKCZgAgEydW1d4TksAuudY3/qqOVkChl1nuKEAgAIGjbFaf////F/XfMu2MtYAX61YfflV3IvFyxlN5FxhyvL/8yjEkAxAIph+AEQA+MPZ+iVQA5lCul7BGkAsmzIBCbf////05+Kba3U59j7GWKFcVGtWtSWle8loETUFW97qlLo7SSkxBUj/8yjEmgyR1lgCUAUoyAHJGFniMVKkh9+j///7orhV3TJP2uWGpEjxE+qRMksqxlbvnlqUHf2nagAolnbs5JwFEZkFhYRmbYz/8yjEogvgIkwAfhIAbW3ZWypif1tf7EjGahfrb/FmGahf/9X//1t6KkxBTUUzLjEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqr/8yjErQwgJkwAS94Aqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqr/8yjEtwwQJkAAe9IAqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqr/8yjEwQrQBiG+EEYAqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo=",
  "stay": "data:audio/mpeg;base64,SUQzBAAAAAAAIlRTU0UAAAAOAAADTGF2ZjYxLjcuMTAzAAAAAAAAAAAAAAD/8yjEAAuIMkD2CYwABKbxCBQzEQFkgh7UmY5GcPl8T638nsG/Ps8uvzh/f08n7Y1/Oco6hv//IKdW9aq/AC220BjbgxQMWg7/8yjEDA0gIrFeCMQCf////8mQKOWH1viEDvqFpwuUQTIBiwSVOUX3nIDKxxkW6/YJ+0TlGvoMMQgerABDkDzy4oZetX///b//8yjEEg0oMlwKSwoEUwXu/Q5uoo8cHYRWoKCqSC0IJHjIdCdJuZRRbdstbahK6k26Kdiwq4JUCohweTUcY///p/+ORPCwo7r/8yjEGAzIKlQAekwgDMUQdG7nrvtA15kuhSNi0ig3jzjvpfewlaQIqj94D5jBygnQmHqz54c2//+j/9cPYqTXu6kQdc1aEn7/8yjEHwzwKlQAY9gAZB9qQ3TEIuMUUY8neQWyxad93xM2OhWxU8kDQJojQfPvLPV///V93QSEpZLFiikMI3WpXcL8Rua6glb/8yjEJgyYIlQBTwAAo1XHbnipBmhG3VKClU3GDNR/C75rIYDT8lzf8cg9CU/xzpGgmf/jDkuyaf/44AugwAFHEbHn//iYEoz/8yjELhfLIoQBjWgAmo0L///6aZKEgSgXseahM////yXNy4XCUHOU0BGx5uJh////+SjOggbrdMvpj3HuS6rbaPa6LRa3W7X/8yjECQ85Ey5fiRAC1mAwAA1eYg5EaeSTFcMsQMNuQQdGZN3chG16u+r9SVdN0rvgxiFfpW9/pfuT39bHt//+KUUAOAwa5oz/8yjEBw8A7t7/zxAAQAbxAw4pkNkDkxRIPlT5SnEqr27U7cbWzVAIV9C9pQFvo/lCiSzRFvLB3/ncDPfGP//6FB1gFVHZ4+v/8yjEBg6QvvJ+EkYipAAKGwwBjWdLUhQVdYwCixaTf+GS+mQZwgwVCaVglaaDwRJH5dD4YSt6iyzQqx+7h8B1BhUtuQAC2Rv/8yjEBg5YFspdQhACwzU4oFyIOB1wi//bAQNKKhoGj0WJEREsFgaHHg0WftPYilXYNPLSrhKdlgqE3Wr////9ClwDh0Jw4mz/8yjEBw6zHmwBjBAAWrHsSzYpntn////+jMf//Vzmb//Y99f/v+gwAp3Y76fdl/1+9XdGIRmt7J/v//2zvO7i0uyDRwBGyKH/8yjEBw7warwBgRAAfdIVt/eiJhgQHulEteIyTxcn+kOxIsPwTIOPDRdLlKP/Iha9am95H1OJpJDpYNNYWFEpCSqVQqmgn1f/8yjEBgyIsr2RzzAApcsgHCLqHGYDkezw5IJ0Q4+YZ/qtg1WEye/nsDrhz7J2m3REoqo8vv//b/RVjSctbcoAwC/iRYAOcuv/8yjEDgyYyv5cXk6KKhRUvPrRwTWoNP1Z9/SRZGnzrCBvCAXsuFzvUho1ZT/////9Kh1n77bvsOcSgrFO5pEKeliachfq/+//8yjEFgw4yyJYVhSKNTo0XhO1uM/cF56ueCMbmPhRnkJDJZDT8n8tfw64LydsZ8PW8YyGsCse2usrA/Gx51nSLJ9Mc1nswgL/8yjEIAwo4sQAm+JoG67IDw/mfbv3ZzM7f///r0p+oJmC/JoOkImLd0hnitli/ncW2s7vMYhY8Xil2ZRIBZZ7nAXu1UO9X+3/8yjEKgzJVsQAlhSk9/n+pN////q0VQAiPagDWQpdM0h5Rts7ploHCgpUO6fu0VgzypfwsEztlRGdc8MepPCCPj2wj5V+7///8yjEMQzxOslgkcTs/+6tAYBUMAYEgG7q8KcHlr3kRp91+udgFfBa3ikW+KSXnP6kfHV1qR2YmyOrR////t///2JOUBKUsMr/8yjEOAxo9tm+C84Q7oBeCDNuGDARvDDPERKt1f//tkvnegykuI4oCZ8+8wS//viAEBhz9f5eOKCeCwwADPhJ9/l+Vvt/X///8yjEQQywUtR8C8QE/ylb2zYUxylN1Vny+rWf9jKwoBGDkdcZw6UANsCSQISP/+O5jAlL//mtlNBJO5HpIbYp0pDJxKl/////8yjESQnrIsGECATcz57L9vb/17//+utFikzpGAAJbRttrIgRoUgty9/+ZkiZNupXuJjQgJHjScDjkk4qHhazpot+qyyHhB3/8yjEXAw7Cr28CAXjR57v/7P/y8hVEtow2H31Cz4xsmObfIUv/P9EuTSWH/5ftOoTBYrOGS2pvvv2Sn/////0FmFXhwiHlRr/8yjEZgzIztZeAIZyyWx0J9RBzbyt/P9r0tTUIFlqQnKhRiTz+ymzeusBF0/9PSuK/PI/+RwauQD+AwYGBhgYAdd/////////8yjEbQwRQuZcCAci///////70M9pWdWZFMrdZv5S9Wt3ZHZDBmQMSRrVO99jTzN7FVcsADiF4XWWc91Z/8Zd+H77ntl6nyX/8yjEdwrxNrVcEAaW/kVz/+hBDparWbxCnOhO9qUWzCKFORnqkhjTHKrZaRzuOUcWVjJ1mjG2ZK2JtorsLdcbO0o4vXuLmrn/8yjEhg0ScnAVQhAAlkFmvH6EPzXRXV1Rhle///z/v/2YgBIkgAIf60ZlEk0zpFaTiI32ATNqTgAYA1ryM//853u6aN6Wa2f/8yjEjBYiakwBmBAB/1o3c1UKCzfePmGgIjf//7Z//mQYjEqRsnSLUVSqA3MJT/QfbSHHPcLirxURhpUDM5X2OFRlKcf00Uz/8yjEbhhScrQBgjAApXFEGKIjtoUTx0jPukBGM7SdwEl9TjwjCoUGm4l4R2fr9hg2Nh1XqTfcg0iR///vocQVR2eHhlJE5GH/8yjERw+Qrtr/wzAAjh1TugKvAcQmDa6tVWoHMBmZQKl09LpmWiTOL0b5SFMouup+Y5lKC8ERublCHgLLq58Ti/z/lXMTGjP/8yjEQxYZIwseDk4e6EK1hFi37pcuteJ0xDo//21////DagdDyLREMKBQB3YBfQncxcWMwKhdm9AlAgCOvmONzC1vb1ECA6z/8yjEJQ+4wvMWk8446YLANOe4pGnoM53I5LNZ3/Zv3///ZEyz51+BiRoCIB/BhCkS4mwePFkJ269Bp3tdxkAsNG0C6d80VW//8yjEIQ0BJt2Ua9TAn+Qs3O+Q/IW2aM3nc9sq//09y9JdpV4fW4DAB/GkRG0Zghfww2ABM9ipjnbT+FHiEJ/Q8cCRq1CX0T7/8yjEKA0ZEy5+a86OT+X9SPPfRhvb///9SkAKG57vbXrwowQL3iyLDa342Bevc+AlBGvWAJN3RZOyUgW/2D34YqpqatV4uir/8yjELgzREt5Ya9Bo8l/kslpqJAeTTcRDAlGrQ3quhgiZJL7kpawMGS17mOrrA3Vw3OGJG7PbBf7ZzBAjUt+z///////1VWT/8yjENQzIrqgoHtgYraAAwH50IPC5pvOTSPrcDt5NxxOO6qAmV/Jd/qpV+BQBEnHH4fy44+8ln8MFP//////6FX5ZCUVG3P7/8yjEPA0Q3tB8k9YwrCDjVNtolECmOFjiyiHrnrpFM43Oq6iGGilBvdv////lMXyH+////65dcsZeXtIn0l2xpekL/+TYqIj/8yjEQgwwqswAm+Ao11kUND9PtEEX/VLa5g2JN8Qk/Z/////a8gFNWv69P//+XYFZkgAGSfYdBJk8q2/RyX/NAKUkQkelnxj/8yjETAywwsgADhYQ6In4ZJlgXhcnW9O45/////////oLseCaWvkEkkAFmzqARcI5N8bY8wpBJve1etoN23ypqjWSETxMHf//8yjEVAwoUtD8DgwG//////9W9aFGgaBWAYEkFt1r0DuflnF7/1gFeN3yKzx5TBLPQXPNQjcOljf7DXEtt1iP/y//0komJAn/8yjEXguwYs26CYYGVQ4BQPrECODAL+G/////////l8MOVym9adSqVP2Vn3K1wbnlsTHjJUBDToKs/2qf//lQ0QUAiMKCUSj/8yjEagvIAtJcCERytEotrNRrAA9wnkHmF9GExbnnAgc/0XN9T2p//r9v872ORjlD6VPz6MKL0D5hq+gwpCK5GuTfaPKhFjT/8yjEdQzhztH/QRACwoOsqIWhRjCr/yXO+MFA6BxSIMKDR453jmWWzuqjRyJRuy2y2Nnv6uNLNRR87vwicgAMIppDTT407qb/8yjEfBgrIs5fhSgAonQzmjYYQAUjnLMSUAdBqZLWZm/UpHz3qb2f2/9aqSKzylugaEmVFB0yeUi4SjTqt1cPht2I04G/IRH/8yjEVhR5huZZ2GgD49RLgPTAxp1PexzSTVaxFekcgMMkClQCtSiRqRfv4Ze4dP+LSJbawXHyEnNDev1Dv+UZfT9m+t9WnI7/8yjEPxFI5v58PlY2/f/+kVfIKmmqa5v4CXX0U4vH9u1k4PqWnlI4lSvncgIB7aA+8dBAzYDSaJQWvygl+Kner/O1scs5Kvn/8yjENA1o5vpYC84WbJUKvHS78AAgPKGyGiqJ56FSWB+enwrVaSY8HMHgp+oVT/Fd+VHi8XP48+N///X9P//9GlUKLKvbZgD/8yjEOQyQ6wJcA9QW+yUE2QiJvSKOVVKbtSWelyc2oFASVZ4OAmIk5wUuyqGPKHIie8p9v/9SQJhakkYAfoDx9T2zZDV5XOX/8yjEQQvouv5YA84W7s2oV63S2s7TwKRP3pDsXeNn83BLteYCDk66SFvfhQSZKZQA7v+A1pD7ABqzeezWE8tZ/SN76+FifVr/8yjETA0A7vJYU9I+o5BGn18bXBxb/6ia+JJr7GAuOvlhWvk5UhXC4kB3GepVUTgAh4OtWmUh7gMyVn1c2FW21evSvYwSBvP/8yjEUwxY/tWQi9A8C3UBQ3E2Rw1nXf//u/Wd//9dDUGKXdtpRBAA/UBuALRTY+gSExLjYC524UIbKNG5piaiK+CmTqbk8hX/8yjEXA0AorhM08pMnN3+yr////WqKqYH5QSF/EaHsi+FAobSV5fbm4kmuy+1yEtAEQD+jj7HXmasONNCcu8TjonU2o7mil//8yjEYwwIqu5eak5i/9sySQADQM7QTABvwcxfOT3f3mIHyOp9v0RQTM5vEUvSgjkKVUNrqVFxnYed////24b1f/sVFPfwO/j/8yjEbQz4msBQDhgUW6id54kSPSthrICkwSuK5UwbSOdd0xECy2d6gWf79jMfPJnCb7+qhjWGtv///+5aEHLV//4A1HEuBUH/8yjEdAzQ5th8C84YiuXHSBrqHohz/zmGP/xPIfhNL/Gm9PX+NMArkHWtynPO6nP/////JiYUcGE0Phh9VZf///rqCDNKhlv/8yjEew0o0sDwy9JMQYe47BaaYj2Y0dv3ibOKN/4AshxQ5Y6JAWy0ibxRT1+91UxYa1jwRb01Chx6qdCt6+rxMLZPZ//9R2X/8yjEgRAQzvJeAt4QyMu/dSyvTQnLLG27QIA+DgcrfJRheJ4D4Mm3ECgIF1uoMxobNwSB+uvx9bXplk1waE6/1i37k3GtEGX/8yjEexGo+uJaA94AMp//+5WNyWxJuSIQAPegD0HlSb2hKMp57iMWtp+j+77NAWt43fjgPWfMElvF7usIAlLIs8smg0GKVk//8yjEbw4RCwpcU9ZCIZDP7P//oRepB1aYp1ZpfaMOPEONNb+qG4U17VkE1Xe2A7KERm9I4CXZgm8TP7t6ff0N9CswxTxjyun/8yjEcQ+xHw5eaw5S+jIZ///76////sWGvTRzUENz5FMCo7keAIxmzzAZHTz0HjGHSoCxdPoC5/AiYdicSW6kWTv+7/+Qjif/8yjEbQ8hSz8eA84auVNUlZZnf4ACgB+4yQjoJ30TANkB+WyMVWGCGHZrOfALLPweteUDXjrpXLbMS//////p0mIbNLdqEID/8yjEawww1w5YCs4eGZfkyKCIq9yHCM1aixzwMZStsiRBpNtUeL0G3QSAVLyj+TfL5f//f//DVQAIZJJHAsAeFmlZTA8V0t//8yjEdQy4uyMeaw5SNntjg5wXGodVmRTx7UCY7mkfv4lPo+RrdU+nT/47Vkd77yGZZBALrMAA/UAIAvOPqYaRai7NxJxwjd//8yjEfQxY7vZcC9QW0f+s7TeEhZP1WFA4grkvl0mlay5I3cTHETQ2L84QwKgUInvCtDmIZsdDVv///qpF+vZ0UpWKmwG6Ya3/8yjEhgyAorZcFo4QeMkH//EGLg/BBiqVBsAEEljjgCsDUONJqgOO/0Ip/3Ejp9SVjgVcesDW7v/qBrNlFtGIMAyGjqf2lQ3/8yjEjwqgStpeg9JCAbqfQgU54G+FzC5woGiVcM5H65W///9WmMYMZeem573nSrZZ2xK8+WCLw4RKHlB07DudLHklrR8lmQj/8yjEnw0gSpAK1hZAJVyQADCEXIR9ge1LUsvu7lSdtLmfmG/vr2U1vN1W7v3duuzNV3fTX1qfSgAJdvt9XJJg0h0EBx7e1a//8yjEpQyoMsW+AMwClmvObCaOrKetn9uW/6NCL/f5Z+lf479v03D6AKluu1kjvAWRwcicyixyLBvqq103Du/55It6//TTnfT/8yjErQz4/ngcSASI/+nRr97fMsaCwFoRH0KgYWOBoFSMSkTaGmg0EgKCRIKBUBIxgFIhMJAVOtLf6yITAXUBWf////9aWj//8yjEtAtoJmB8GlIA/8ZVTEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/8yjEwQqgJnZeCMYAVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/8yjE0QqgHm2+CMIAVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/8yjE4QyIQhgASZIAVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVU=",
  "wait": "data:audio/mpeg;base64,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",
  "bye": "data:audio/mpeg;base64,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"
};
"""

LIVE = r"""
(() => {
  "use strict";
  const base = new URL("./", document.currentScript.src);
  const socketURL = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContentConstrained";
  const Audio = window.AudioContext || window.webkitAudioContext;

  async function startGemini({ endpoint, code, lang, preview, signal, onState, onFallback }) {
    if (!Audio || (!preview && (!window.AudioWorkletNode || !navigator.mediaDevices?.getUserMedia))) {
      onFallback("Live microphone audio is unavailable on this device.");
      return;
    }
    const context = new Audio();
    const activeAudio = new Set();
    const sessionAbort = new AbortController();
    let stream, socket, source, worklet, timer, finish, next = 0, ready = false, muted = false, stopped = false;
    const stopPlayback = () => {
      for (const audio of activeAudio) {
        audio.onended = null;
        audio.stop();
      }
      activeAudio.clear();
      next = 0;
    };
    function stop() {
      if (stopped) return;
      stopped = true;
      sessionAbort.abort();
      signal.removeEventListener("abort", stop);
      clearTimeout(timer);
      clearTimeout(finish);
      stopPlayback();
      worklet?.disconnect();
      source?.disconnect();
      stream?.getTracks().forEach(track => track.stop());
      if (socket && socket.readyState < WebSocket.CLOSING) socket.close();
      context.close().catch(() => {});
    }
    function fail(message) {
      if (stopped) return;
      stop();
      onFallback(message);
    }
    function send(message) {
      if (socket?.readyState === WebSocket.OPEN) socket.send(JSON.stringify(message));
    }
    signal.addEventListener("abort", stop, { once: true });
    if (signal.aborted) {
      stop();
      return;
    }
    timer = setTimeout(() => fail("Live voice timed out. Use the call replies below."), 16000);

    try {
      await context.resume();
      if (stopped) return;
      if (!preview) {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
        });
        if (stopped) {
          stream.getTracks().forEach(track => track.stop());
          return;
        }
        await context.audioWorklet.addModule(new URL("mic-worklet.js?v=1", base));
        if (stopped) return;
      }
      const tokenURL = new URL(endpoint);
      tokenURL.searchParams.set("lang", lang);
      const response = await fetch(tokenURL, {
        method: "POST",
        headers: { Authorization: "Bearer " + code },
        signal: sessionAbort.signal,
        cache: "no-store",
        redirect: "error",
      });
      if (response.status === 401) return fail("That demo code did not match. The call replies are still available.");
      if (response.status === 429) return fail("Live voice limit reached. Use the call replies below.");
      if (!response.ok) return fail("Live voice is unavailable. Use the call replies below.");
      const { token, setup } = await response.json();
      if (!token || !setup || stopped) return fail("Live voice is unavailable. Use the call replies below.");
      socket = new WebSocket(socketURL + "?access_token=" + encodeURIComponent(token));
      socket.binaryType = "arraybuffer";
      socket.onopen = () => send({ setup });
      socket.onerror = () => fail("Live voice disconnected. Use the call replies below.");
      socket.onclose = () => fail("Live voice disconnected. Use the call replies below.");
      socket.onmessage = (event) => {
        if (stopped) return;
        let message;
        try {
          message = JSON.parse(typeof event.data === "string" ? event.data : new TextDecoder().decode(event.data));
        } catch {
          return;
        }
        if (message.setupComplete && !ready) {
          ready = true;
          clearTimeout(timer);
          finish = setTimeout(() => fail("Live voice finished. You can stay on the call with the replies below."), 150000);
          send({ realtimeInput: { text: "Start the simulated call with a short hello in the selected language." } });
          if (preview) {
            onState("Gemini voice preview · mic off");
            return;
          }
          source = context.createMediaStreamSource(stream);
          worklet = new AudioWorkletNode(context, "safelink-mic", { channelCount: 1, channelCountMode: "explicit" });
          worklet.port.onmessage = ({ data }) => {
            if (stopped || muted || socket.bufferedAmount > 128000) return;
            send({ realtimeInput: { audio: { mimeType: "audio/pcm;rate=16000", data: btoa(String.fromCharCode(...data)) } } });
          };
          source.connect(worklet).connect(context.destination);
          onState("Live voice · mic on", (nextMuted) => {
            muted = nextMuted;
            stream.getAudioTracks().forEach(track => { track.enabled = !muted; });
            if (muted) send({ realtimeInput: { audioStreamEnd: true } });
          });
        }
        const content = message.serverContent;
        if (content?.interrupted) stopPlayback();
        for (const part of content?.modelTurn?.parts || []) {
          const blob = part.inlineData;
          if (!blob?.mimeType?.startsWith("audio/pcm") || !blob.data) continue;
          const bytes = Uint8Array.from(atob(blob.data), x => x.charCodeAt(0));
          const rate = Number(blob.mimeType.match(/rate=(\d+)/)?.[1]) || 24000;
          const view = new DataView(bytes.buffer), length = bytes.length >> 1;
          if (!length) continue;
          const buffer = context.createBuffer(1, length, rate);
          const samples = buffer.getChannelData(0);
          for (let i = 0; i < length; i++) samples[i] = view.getInt16(i * 2, true) / 32768;
          const audio = context.createBufferSource();
          audio.buffer = buffer;
          audio.connect(context.destination);
          activeAudio.add(audio);
          onState(null, undefined, true);
          audio.onended = () => activeAudio.delete(audio);
          next = Math.max(context.currentTime + 0.02, next);
          audio.start(next);
          next += buffer.duration;
        }
        if (message.goAway) fail("Live voice is ending. The call replies are ready.");
      };
    } catch (error) {
      const micDenied = error.name === "NotAllowedError" || error.name === "NotFoundError";
      fail(micDenied ? "Microphone unavailable. Use the call replies below." : "Could not connect live voice. Use the call replies below.");
    }
  }
  window.safeLinkLiveVoice = startGemini;
})();
"""

UPGRADE = r"""
(() => {
  "use strict";
  const base = new URL("./", document.currentScript.src);
  const endpoint = document.currentScript.dataset.voiceEndpoint;
  const el = id => document.getElementById(id);
  const settings = el("ride-settings"), screen = el("ride-screen"), form = el("ride-form");
  const audio = new Audio();
  let plan, session, mute, muted = false;
  const lines = {
    en: {
      hello: "Hello. I am here. Can you hear me?",
      stay: "Of course. I will stay on the line.",
      wait: "Take your time. I am still here.",
      bye: "Okay. Talk to you soon.",
    },
    ta: {
      hello: "ஹலோ, நான் பேசுறேன். கேட்குதா?",
      stay: "சரி, நான் லைனிலேயே இருக்கேன்.",
      wait: "அவசரம் இல்லை. நான் லைனில் இருக்கேன்.",
      bye: "சரி, அப்புறம் பேசலாம்.",
    },
  };

  el("ride-title").textContent = "Ride call";
  settings.querySelector(":scope > form > p").textContent = "Stage an incoming call with a voice that can stay on the line.";
  el("ride-pickup").textContent = "";
  el("ride-pickup").setAttribute("role", "status");
  el("ride-pickup").classList.add("call-status");
  el("ride-pickup").insertAdjacentHTML("afterend", `
    <div id="call-voice-tools" class="call-voice-tools" hidden>
      <button type="button" id="call-mute" class="call-mute" aria-pressed="false" hidden>Mute mic</button>
      <div class="call-replies" role="group" aria-label="Play a staged reply">
        <button type="button" data-line="stay">Stay on the line</button>
        <button type="button" data-line="wait">Give me a moment</button>
        <button type="button" data-line="bye">Talk soon</button>
      </div>
      <p id="call-caption" class="call-caption" role="status"></p>
    </div>`);
  el("ride-ring").closest("label").insertAdjacentHTML("beforebegin", `
    <div class="ride-fields call-options">
      <label for="call-mode">Voice<select id="call-mode">
        <option value="offline">Offline replies</option>
        <option value="live">Gemini Live</option>
        <option value="silent">Silent screen</option>
      </select></label>
      <label for="call-language">Language<select id="call-language">
        <option value="en">English</option>
        <option value="ta">தமிழ்</option>
        <option value="mixed">Tanglish</option>
      </select></label>
    </div>
    <div id="call-cloud" class="call-cloud" hidden>
      <label for="call-code">Demo access code
        <input id="call-code" maxlength="128" type="password" autocomplete="off" spellcheck="false">
      </label>
      <label class="ride-audio call-preview"><input id="call-preview" type="checkbox"> Preview voice with mic off</label>
      <p id="call-privacy">Answering uses your microphone and streams audio to Google. Free-tier inputs may be used to improve Google’s products. Use fictional details.</p>
    </div>`);
  el("ride-ring").closest("label").insertAdjacentHTML("afterend", '<p id="call-setup-note" class="ride-meta" role="status"></p>');
  form.querySelector(".ride-meta:last-child").textContent = "Simulated call only. Use SOS to reach real help. Keep SafeLink open for a scheduled ring.";

  const mode = el("call-mode"), language = el("call-language"), code = el("call-code");
  function describeMode() {
    const live = mode.value === "live";
    el("call-cloud").hidden = !live || !endpoint;
    code.required = live && !!endpoint;
    language.querySelector('[value="mixed"]').hidden = !live;
    if (!live && language.value === "mixed") language.value = "en";
    el("call-setup-note").textContent = live
      ? (endpoint ? "Live voice uses internet. Offline replies are available if the connection drops." : "Gemini Live is awaiting server setup. This call will use offline replies.")
      : mode.value === "offline" && language.value === "ta" ? "Tamil audio needs a Tamil voice installed. Replies also appear on screen." : "";
  }
  const preview = el("call-preview");
  preview.addEventListener("change", () => {
    el("call-privacy").textContent = preview.checked
      ? "This preview sends a sample line to Gemini. The microphone stays off."
      : "Answering uses your microphone and streams audio to Google. Free-tier inputs may be used to improve Google’s products. Use fictional details.";
  });
  mode.addEventListener("change", describeMode);
  language.addEventListener("change", describeMode);
  describeMode();

  function pauseVoice() {
    audio.pause();
    window.speechSynthesis?.cancel();
  }
  function say(key) {
    if (!plan) return;
    const lang = plan.lang === "ta" ? "ta" : "en";
    const text = lines[lang][key];
    el("call-caption").textContent = text;
    el("call-caption").lang = lang;
    pauseVoice();
    if (lang === "en" && window.safeLinkRideClips?.[key]) {
      audio.src = window.safeLinkRideClips[key];
      audio.play().catch(() => {});
      return;
    }
    if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) return;
    const voice = speechSynthesis.getVoices().find(candidate => candidate.localService && candidate.lang.toLowerCase().startsWith(lang));
    if (!voice) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.lang = voice.lang;
    speechSynthesis.speak(utterance);
  }
  function wipeSession() {
    session?.abort();
    session = null;
    mute = null;
    muted = false;
    pauseVoice();
    el("call-mute").hidden = true;
    el("call-mute").textContent = "Mute mic";
    el("call-mute").setAttribute("aria-pressed", "false");
    el("call-caption").textContent = "";
    screen.removeAttribute("data-live");
    screen.removeAttribute("data-audio");
    if (plan) plan.code = "";
    plan = null;
  }
  form.addEventListener("submit", () => {
    wipeSession();
    plan = { mode: mode.value, lang: language.value, code: code.value.trim(), preview: preview.checked };
    code.value = "";
  }, { capture: true });
  settings.addEventListener("close", () => { code.value = ""; });
  el("ride-answer").addEventListener("click", () => {
    const selected = plan || { mode: "offline", lang: "en" };
    const tools = el("call-voice-tools"), label = el("ride-pickup");
    const replies = tools.querySelector(".call-replies");
    tools.hidden = selected.mode === "silent";
    label.hidden = selected.mode === "silent";
    if (selected.mode === "silent") return;
    const fallback = (message, hello = false) => {
      if (!screen.open || plan !== selected) return;
      label.textContent = message;
      replies.hidden = false;
      el("call-mute").hidden = true;
      screen.removeAttribute("data-live");
      if (hello) say("hello");
    };
    if (selected.mode !== "live" || !endpoint || !navigator.onLine || !window.safeLinkLiveVoice) {
      fallback("Offline replies", true);
      return;
    }
    label.textContent = "Connecting live voice…";
    replies.hidden = true;
    session = new AbortController();
    const access = selected.code;
    selected.code = "";
    window.safeLinkLiveVoice({
      endpoint, code: access, lang: selected.lang, preview: selected.preview, signal: session.signal,
      onState(message, toggle, audioReceived) {
        if (audioReceived) {
          screen.dataset.audio = "received";
          if (selected.preview) label.textContent = "Gemini replied · mic off";
          return;
        }
        label.textContent = message;
        el("call-mute").hidden = !toggle;
        screen.dataset.live = "true";
        mute = toggle;
      },
      onFallback: fallback,
    }).catch(() => fallback("Live voice is unavailable. Use the call replies below."));
  });
  el("call-mute").addEventListener("click", () => {
    if (!mute) return;
    muted = !muted;
    mute(muted);
    el("ride-pickup").textContent = muted ? "Live voice · mic muted" : "Live voice · mic on";
    el("call-mute").textContent = muted ? "Unmute mic" : "Mute mic";
    el("call-mute").setAttribute("aria-pressed", String(muted));
  });
  for (const button of screen.querySelectorAll("[data-line]")) {
    button.addEventListener("click", () => say(button.dataset.line));
  }
  for (const id of ["ride-cancel", "ride-decline", "ride-hangup"]) el(id).addEventListener("click", wipeSession);
  screen.addEventListener("cancel", wipeSession);
  screen.addEventListener("close", () => { if (!screen.open) wipeSession(); });
  window.addEventListener("pagehide", wipeSession);
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden || !session || session.signal.aborted) return;
    session.abort();
    mute = null;
    el("call-mute").hidden = true;
    screen.removeAttribute("data-live");
    el("ride-pickup").textContent = "Live voice stopped while SafeLink was in the background.";
    screen.querySelector(".call-replies").hidden = false;
  });

  const top = el("app-brand").closest("header");
  top.classList.add("safelink-upgrade");
  top.insertAdjacentHTML("afterend", `
    <nav class="safelink-dock" aria-label="Quick actions">
      <button type="button" data-jump="state"><span aria-hidden="true">⌖</span>Plan</button>
      <button type="button" data-jump="journey"><span aria-hidden="true">↓</span>Offline</button>
      <button type="button" data-jump="ride"><span aria-hidden="true">◉</span>Ride call</button>
      <button type="button" data-jump="sos"><span aria-hidden="true">!</span>SOS</button>
    </nav>`);
  el("workspace").querySelector(".workspace-nav").insertAdjacentHTML("afterend", `
    <div class="safelink-connectivity aa-width">
      <span id="safelink-network"></span>
      <span id="safelink-cache" role="status" hidden></span>
    </div>`);
  document.body.classList.add("safelink-has-dock");
  for (const button of document.querySelectorAll(".safelink-dock button")) {
    button.addEventListener("click", () => {
      const jump = button.dataset.jump;
      if (jump === "ride" || jump === "sos") {
        el(jump === "sos" ? "top-sos" : "ride-open").click();
      } else {
        el(jump + "-tab").click();
        el(jump === "state" ? "workspace" : "journey").scrollIntoView({ block: "start" });
      }
    });
  }
  function networkStatus() {
    const badge = el("safelink-network");
    badge.textContent = navigator.onLine ? "Connected to a network" : "Offline · Trichy maps and ride replies available";
    badge.dataset.online = String(navigator.onLine);
  }
  window.addEventListener("online", networkStatus);
  window.addEventListener("offline", networkStatus);
  networkStatus();

  const appRoot = new URL("../", base);
  if ("serviceWorker" in navigator && location.protocol !== "file:" &&
      (location.pathname === appRoot.pathname || location.pathname === appRoot.pathname + "index.html")) {
    navigator.serviceWorker.register(new URL("safelink-sw.js", appRoot), { scope: appRoot.pathname })
      .then(() => navigator.serviceWorker.ready)
      .then(async () => {
        const cache = await caches.open("safelink-kit-v1:" + appRoot.pathname);
        if (!await cache.match(appRoot)) return;
        const status = el("safelink-cache");
        status.textContent = "Offline kit saved";
        status.hidden = false;
      })
      .catch(() => {});
  }
})();
"""

WORKLET = r"""
class SafeLinkMic extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bytes = new Uint8Array(1280);
    this.view = new DataView(this.bytes.buffer);
    this.offset = 0;
    this.phase = 0;
    this.sum = 0;
    this.count = 0;
  }
  process(inputs) {
    const input = inputs[0]?.[0];
    if (!input) return true;
    for (const sample of input) {
      this.sum += sample;
      this.count++;
      this.phase += 16000;
      if (this.phase < sampleRate) continue;
      const bounded = Math.max(-1, Math.min(1, this.sum / this.count));
      this.view.setInt16(this.offset, Math.round(bounded * (bounded < 0 ? 32768 : 32767)), true);
      this.offset += 2;
      this.phase -= sampleRate;
      this.sum = 0;
      this.count = 0;
      if (this.offset === this.bytes.length) {
        this.port.postMessage(this.bytes);
        this.offset = 0;
      }
    }
    return true;
  }
}
registerProcessor("safelink-mic", SafeLinkMic);
"""

OFFLINE = r"""
"use strict";
const home = new URL("./", self.location.href);
const cacheKey = "safelink-kit-v1:" + home.pathname;
const assetURLs = [new URL("mic-worklet.js?v=1", home).href];
const pagePaths = [home.pathname, home.pathname + "index.html"];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(cacheKey).then(async cache => {
    await cache.addAll([home.href, ...assetURLs]);
    await self.skipWaiting();
  }));
});
self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const oldKeys = (await caches.keys()).filter(key => /^safelink-kit-v\d+:/.test(key) &&
      key.slice(key.indexOf(":") + 1) === home.pathname && key !== cacheKey);
    await Promise.all(oldKeys.map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});
self.addEventListener("fetch", event => {
  const request = event.request, url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== home.origin) return;
  if (request.mode === "navigate" && pagePaths.includes(url.pathname)) {
    event.respondWith((async () => {
      try {
        return await fetch(request);
      } catch {
        return await (await caches.open(cacheKey)).match(home) || Response.error();
      }
    })());
  } else if (assetURLs.includes(url.href)) {
    event.respondWith(caches.open(cacheKey).then(async cache => (await cache.match(request)) || fetch(request)));
  }
});
"""

app = Path("index.html")
atlas = app.read_text(encoding="utf-8")
if "<!doctype html>" not in atlas.lower() or atlas.count("</head>") != 1 or atlas.count("</body>") != 1:
    raise SystemExit("Expected a standalone atlas in index.html")

site_base = 'new URL("./", location.href)'
asset_base = 'new URL("./", document.currentScript.src)'
voice_endpoint = escape(VOICE_ENDPOINT, quote=True)
live = LIVE.replace(asset_base, site_base)
upgrade = UPGRADE.replace(asset_base, site_base).replace('new URL("../", base)', 'base')
scripts = f'<script>{CLIPS}</script><script>{live}</script><script data-voice-endpoint="{voice_endpoint}">{upgrade}</script>'
atlas = atlas.replace("</head>", f"<style>{STYLE}</style>\n</head>", 1)
atlas = atlas.replace("</body>", scripts + "\n</body>", 1)
app.write_text(atlas, encoding="utf-8")
Path("mic-worklet.js").write_text(WORKLET, encoding="utf-8")
Path("safelink-sw.js").write_text(OFFLINE, encoding="utf-8")
