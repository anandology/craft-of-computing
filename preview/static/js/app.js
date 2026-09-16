// Renders Jupyter notebooks fetched as JSON, and keeps them current.
//
// A notebook is only re-rendered when what came back differs from what is
// already on screen. The page polls every few seconds and most polls return
// what we have, so re-rendering regardless would reset the reader's scroll
// position under them every few seconds.

const lastRendered = {};

async function getNotebook(url) {
    const response = await fetch(url, {cache: "no-store"});
    if (!response.ok) {
        throw new Error(`${response.status} from ${url}`);
    }
    return await response.json();
}

async function renderNotebookAsync(selector, url) {
    const holder = document.querySelector(selector);
    if (!holder) {
        return;
    }

    const ipynb = await getNotebook(url);
    const serialized = JSON.stringify(ipynb);
    if (lastRendered[selector] === serialized) {
        return;
    }
    const isFirstRender = !(selector in lastRendered);
    lastRendered[selector] = serialized;

    const notebook = nb.parse(ipynb);
    while (holder.hasChildNodes()) {
        holder.removeChild(holder.lastChild);
    }
    holder.appendChild(notebook.render());
    Prism.highlightAll();

    if (!isFirstRender) {
        flash(holder);
    }
}

// Marks a notebook that just changed, so a page of 40 of them shows who is
// working without having to be read top to bottom.
function flash(holder) {
    const wrapper = holder.closest(".notebook-wrapper");
    if (!wrapper) {
        return;
    }
    wrapper.classList.remove("updated");
    void wrapper.offsetWidth;  // restart the transition if it is still running
    wrapper.classList.add("updated");
    setTimeout(() => wrapper.classList.remove("updated"), 3000);
}

function renderNotebook(selector, url) {
    renderNotebookAsync(selector, url).catch(err => console.error(err));
}

function watchNotebook(selector, url, seconds) {
    renderNotebook(selector, url);
    setInterval(() => renderNotebook(selector, url), seconds * 1000);
}
