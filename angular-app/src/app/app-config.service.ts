import { Injectable } from '@angular/core';
import { environment } from '../environments/environment';
import { LOCAL_API_URL, resolveApiUrl } from '../environments/runtime-config';

@Injectable({ providedIn: 'root' })
export class AppConfigService {
  private apiUrl = environment.apiUrl || LOCAL_API_URL;

  load(): void {
    this.apiUrl = resolveApiUrl(this.apiUrl || LOCAL_API_URL);
  }

  getApiUrl(): string {
    return this.apiUrl;
  }
}
