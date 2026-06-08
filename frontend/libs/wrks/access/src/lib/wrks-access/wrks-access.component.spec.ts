import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksAccessComponent } from './wrks-access.component';

describe('WrksAccessComponent', () => {
  let component: WrksAccessComponent;
  let fixture: ComponentFixture<WrksAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
