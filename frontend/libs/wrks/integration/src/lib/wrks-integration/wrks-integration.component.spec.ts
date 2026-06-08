import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksIntegrationComponent } from './wrks-integration.component';

describe('WrksIntegrationComponent', () => {
  let component: WrksIntegrationComponent;
  let fixture: ComponentFixture<WrksIntegrationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksIntegrationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksIntegrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
