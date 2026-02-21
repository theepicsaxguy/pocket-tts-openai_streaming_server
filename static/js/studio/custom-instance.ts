/**
 * Orval custom Axios mutator.
 * Replaces the Proxy-based wrapper — Orval calls this directly,
 * so generated functions return data (not AxiosResponse).
 */

import Axios from 'axios';
import type { AxiosError, AxiosRequestConfig } from 'axios';

export const AXIOS_INSTANCE = Axios.create();

export const customInstance = <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig,
): Promise<T> => {
  const source = Axios.CancelToken.source();
  const promise = AXIOS_INSTANCE({
    ...config,
    ...options,
    cancelToken: source.token,
  }).then(({ data }) => data);

  // @ts-ignore — Orval attaches cancel for query libraries
  promise.cancel = () => source.cancel('Query was cancelled');

  return promise;
};

export default customInstance;

export type ErrorType<Error> = AxiosError<Error>;
export type BodyType<BodyData> = BodyData;
