/**
 *
 * Asynchronously loads the component for CanonicalPage
 *
 */

import Loadable from "react-loadable";

export default Loadable({
  loader: () => import("./index"),
  loading: () => null
});
