import axios from "axios";

const host = "http://localhost:8000"


export async function onNodeClick(nodeName: string) {
    await axios.get(host + `/getNode?node_name=${nodeName}`)
       .then((response) => {
            // Do something
            console.log(response);
            const nodeResult = response.data.result;
            //return nodeResult

    })
}